__all__ = [
    'PreconfigurationFile',
    'CommandSequence',
    'Install',
    'Append',
    'Copy',
    'Sed',
    'a',
    'i',
    's',
    'regexp',
    'Chdir',
    'Packages',
    'LoadTests',
    'assert_sorted',
    'chain',
]

import contextlib
import io
import os.path
import pathlib
import re
import shlex
import subprocess
import unittest
import unittest.mock

echo_re = re.compile(r'''
\\\\|\\a|\\b|\\c|\\e|\\f|\\n|\\r|\\t|\\v
|
\\0[0-9]{1,3}
|
\\x[0-9A-Fa-f]{1,2}
|
\\\n
''', re.VERBOSE)


def uniquify(seq):
  return [
      seq[i]
      for i in sorted({elem: -1 - i
                       for i, elem in enumerate(reversed(seq))}.values())
  ]


class PreconfigurationFile(list):

  def __init__(self, iterable):
    super().__init__(iterable)
    for owner, question_name, question_type, value in self:
      try:
        value.preconfiguration_file = self
      except AttributeError:
        pass

  @property
  def lines(self):
    for owner, question_name, question_type, value in self:
      value = f'{value}'
      assert '\n' not in value.replace(r'\\', '').replace('\\\n', '')
      yield f'{owner} {question_name} {question_type} {value}'

  def __str__(self):
    return '\n'.join(self.lines)

  @property
  def desktop(self):
    result, = [
        value for owner, question_name, question_type, value in self
        if owner == 'tasksel' and question_name == 'tasksel/desktop'
    ]
    return result


class CommandSequence(list):

  def __init__(self, iterable):
    super().__init__(iterable)
    for command in self:
      try:
        command.command_sequence = self
      except AttributeError:
        pass

  @property
  def mkdir_paths(self):
    for command in self:
      dest = getattr(command, 'dest', None)
      if dest is not None and dest.startswith('/target/home/'):
        parts = pathlib.Path(dest).parts
        if len(parts) >= 6:
          yield os.path.dirname(dest)

  @property
  def chown_paths(self):
    for command in self:
      dest = getattr(command, 'dest', None)
      if dest is not None and dest.startswith('/target/home/'):
        parts = pathlib.Path(dest).parts
        if len(parts) >= 5:
          yield os.path.join(*parts[:5])

  def __str__(self):
    result = ';'.join(f'{command}' for command in self)
    paths = list(self.mkdir_paths)
    if paths:
      paths = uniquify(paths)
      result = 'mkdir -p ' + ' '.join(
          shlex.quote(filename) for filename in paths
          if not any(
              other_filename.startswith(f'{filename}/')
              for other_filename in paths)) + ';' + result
    paths = list(self.chown_paths)
    if paths:
      paths = uniquify(paths)
      result += ';chown -R 1000:1000 ' + ' '.join(
          shlex.quote(filename) for filename in paths)
    return result


class Install:

  def __init__(self, text, filename, mode=None):
    if isinstance(text, io.TextIOBase):
      with text:
        assert os.path.basename(filename) != os.path.basename(text.name)
        self.text = text.read()[:-1]
      self.dest = os.path.join(
          os.path.dirname(filename),
          os.path.basename(filename) or os.path.basename(text.name))
    else:
      self.text = text
      self.dest = filename
    self.mode = mode
    LoadTests.registry.append(self)

  def __str__(self):
    text = echo_re.sub(r'\\\g<0>', self.text).replace('\n', r'\n')
    result = f'echo -e {shlex.quote(text)} > {shlex.quote(self.dest)}'
    if self.mode is not None:
      result += f';chmod {shlex.quote(self.mode)} {shlex.quote(self.dest)}'
    return result

  def load_tests(self, loader, tests, pattern):
    if self.dest.startswith('/target/'):
      yield from loader.loadTestsFromTestCase(
          type('InstallTestCase', (InstallTestCase,), dict(command=self)))


class InstallTestCase(unittest.TestCase):

  def runTest(self):
    a = f'{self.command.text}\n'
    with open(self.command.dest[len('/target'):]) as f:
      b = f.read()
    self.assertEqual(a, b)

  def __str__(self):
    return f'{super().__str__()} {self.command.dest}'


class Append:

  def __init__(self, text, filename):
    self.text = text
    self.filename = filename
    LoadTests.registry.append(self)

  def __str__(self):
    text = echo_re.sub(r'\\\g<0>', self.text).replace('\n', r'\n')
    return f'echo -e {shlex.quote(text)} >> {shlex.quote(self.filename)}'

  def load_tests(self, loader, tests, pattern):
    if self.filename.startswith('/target/'):
      yield from loader.loadTestsFromTestCase(
          type('AppendTestCase', (AppendTestCase,), dict(command=self)))


class AppendTestCase(unittest.TestCase):

  def runTest(self):
    a = f'{self.command.text}\n'
    with open(self.command.filename[len('/target'):]) as f:
      b = f.read()[-len(a):]
    self.assertEqual(a, b)

  def __str__(self):
    return f'{super().__str__()} {self.command.filename}'


class Copy:

  def __init__(self, source, dest):
    assert os.path.basename(source) != os.path.basename(dest)
    self.source = source
    self.dest = dest
    LoadTests.registry.append(self)

  def __str__(self):
    return f'cp {shlex.quote(self.source)} {shlex.quote(self.dest)}'

  def load_tests(self, loader, tests, pattern):
    if self.source.startswith('/target/') and self.dest.startswith('/target/'):
      dest = os.path.join(
          os.path.dirname(self.dest),
          os.path.basename(self.dest) or os.path.basename(self.source))
      command_sequence = getattr(self, 'command_sequence', None)
      if command_sequence is not None and not any(
          isinstance(command, Sed) and command.filename == dest
          for command in command_sequence):
        yield from loader.loadTestsFromTestCase(
            type('CopyTestCase', (CopyTestCase,), dict(command=self)))


class CopyTestCase(unittest.TestCase):

  def runTest(self):
    with open(self.command.source[len('/target'):]) as f:
      a = f.read()
    dest = os.path.join(
        os.path.dirname(self.command.dest),
        os.path.basename(self.command.dest) or
        os.path.basename(self.command.source))
    with open(dest[len('/target'):]) as f:
      b = f.read()
    self.assertEqual(a, b)

  def __str__(self):
    dest = os.path.join(
        os.path.dirname(self.command.dest),
        os.path.basename(self.command.dest) or
        os.path.basename(self.command.source))
    return f'{super().__str__()} {dest}'


class Sed:

  def __init__(self, script, filename):
    self.script = script
    self.filename = filename
    LoadTests.registry.append(self)

  def __str__(self):
    script = echo_re.sub(r'\\\g<0>', self.script).replace('\n', r'\n')
    return f'echo -e {shlex.quote(script)} | sed -f - -i {shlex.quote(self.filename)}'

  def load_tests(self, loader, tests, pattern):
    if self.filename.startswith('/target/'):
      yield from loader.loadTestsFromTestCase(
          type('SedTestCase', (SedTestCase,), dict(command=self)))

  @property
  def input(self):
    command_sequence = getattr(self, 'command_sequence', None)
    if command_sequence is not None:
      for command in command_sequence:
        if isinstance(command, Copy) and command.source.startswith('/target/'):
          dest = os.path.join(
              os.path.dirname(command.dest),
              os.path.basename(command.dest) or
              os.path.basename(command.source))
          if dest == self.filename:
            return command.source[len('/target'):]


class SedTestCase(unittest.TestCase):

  def test_wasnt_equal(self):
    with open(self.command.input) as f:
      a = f.read()
    with open(self.command.filename[len('/target'):]) as f:
      b = f.read()
    self.assertNotEqual(a, b)

  def test_made_equal(self):
    args = ['sed', self.command.script, self.command.input]
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
      with io.TextIOWrapper(p.stdout) as f:
        a = f.read()
    with open(self.command.filename[len('/target'):]) as f:
      b = f.read()
    self.assertEqual(a, b)

  def __str__(self):
    return f'{super().__str__()} {self.command.filename}'


def a(text):
  return r'''a \
{}'''.format(text.replace('\\', r'\\').replace('\n', '\\\n'))


def i(text):
  return r'''i \
{}'''.format(text.replace('\\', r'\\').replace('\n', '\\\n'))


def s(regexp, replacement):
  return 's/{}/{}/'.format(
      regexp.replace('/', r'\/'), replacement.replace('/', r'\/'))


def regexp(regexp):
  return '/{}/'.format(regexp.replace('/', r'\/'))


class Chdir:

  def __init__(self, filename):
    self.dest = f'{filename}/'

  def __str__(self):
    return f'cd {shlex.quote(os.path.dirname(self.dest))}'


apt_cache = None


def get_cache():
  global apt_cache
  if apt_cache is None:
    import apt
    apt_cache = apt.Cache()
  return apt_cache


dependencies_cache = {}


def dependencies_from_version(version, dependency_fields: frozenset, visited):
  result = dependencies_cache.get((version.package.name, dependency_fields))
  if result is None:
    dependencies = set()
    dependencies_cache[version.package.name,
                       dependency_fields] = visited, dependencies
  else:
    intersection, dependencies = result
    if intersection <= visited:
      return dependencies
    intersection &= visited
  visited = visited | {version.package.name}
  result = [
      dependencies_from_or_group(or_group, dependency_fields, visited)
      for or_group in version.get_dependencies(*dependency_fields)
  ]
  dependencies.update(*result)
  return dependencies


def dependencies_from_or_group(or_group, dependency_fields, visited):
  if visited.isdisjoint(
      version.package.name
      for dependency in or_group for version in dependency.target_versions):
    result = [
        dependencies_from_version(version, dependency_fields, visited)
        | {version.package.name}
        for dependency in or_group for version in dependency.target_versions
    ]
    if result:
      return set.intersection(*result)
  return set()


def get_dependencies(package_name, dependency_fields):
  package = get_cache()[package_name]
  result = [
      dependencies_from_version(version, dependency_fields, set())
      for version in package.versions
  ]
  return set.intersection(*result)


man_packages = None


def get_man_packages():
  global man_packages
  if man_packages is None:
    args = ['apt-file', '-l', 'search', '/usr/share/man/']
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
      with io.TextIOWrapper(p.stdout) as f:
        text = f.read()
    man_packages = text.splitlines()
  return man_packages


class Packages(list):

  def __init__(self, iterable):
    super().__init__(iterable)
    self += sorted(self.man_packages)
    assert len(self) == len(set(self))
    LoadTests.registry.append(self)

  def __str__(self):
    return ' '.join(self)

  def load_tests(self, loader, tests, pattern):
    for package_name in self:
      yield from loader.loadTestsFromTestCase(
          type('PackageTestCase', (PackageTestCase,),
               dict(package_name=package_name, packages=self)))
    result = [
        get_dependencies(package_name, self.dependency_fields)
        for package_name in self
    ]
    dependencies = set.union(*result).difference(self)
    preconfiguration_file = getattr(self, 'preconfiguration_file', None)
    if preconfiguration_file is not None:
      dependencies -= get_dependencies(
          f'task-{preconfiguration_file.desktop}-desktop',
          self.dependency_fields)
    for package_name in dependencies:
      package = get_cache()[package_name]
      if self.install_priorities.isdisjoint(
          version.priority for version in package.versions):
        yield from loader.loadTestsFromTestCase(
            type('DependencyTestCase', (DependencyTestCase,),
                 dict(package_name=package_name, packages=self)))

  dependency_fields = frozenset([
      'Depends',
      'Pre-Depends',
      'Recommends',
  ])
  install_priorities = {
      'required',
      'important',
      'standard',
  }

  @property
  def man_packages(self):
    result = [
        get_dependencies(package_name, self.dependency_fields)
        for package_name in set(self).intersection(get_cache().keys())
    ]
    doc_packages = {
        f'{package_name}-doc'
        for package_name in set.union(*result, self)
    }.intersection(get_cache().keys())
    man_packages = doc_packages.intersection(get_man_packages())
    reverse_dependencies = {
        package_name
        for package_name in doc_packages
        if package_name in man_packages or not get_dependencies(
            package_name, self.dependency_fields).isdisjoint(man_packages)
    }
    return reverse_dependencies.difference(
        other_name
        for package_name in
        reverse_dependencies for other_name in get_dependencies(
            package_name, self.dependency_fields) & reverse_dependencies
        if package_name not in get_dependencies(other_name,
                                                self.dependency_fields))


class PackageTestCase(unittest.TestCase):

  def test_necessary(self):
    a = self.package_name
    for other_name in self.packages:
      if other_name != self.package_name:
        b = get_dependencies(other_name, self.packages.dependency_fields)
        self.assertNotIn(a, b, other_name)
    preconfiguration_file = getattr(self.packages, 'preconfiguration_file',
                                    None)
    if preconfiguration_file is not None:
      other_name = f'task-{preconfiguration_file.desktop}-desktop'
      b = get_dependencies(other_name, self.packages.dependency_fields)
      self.assertNotIn(a, b, other_name)

  def test_priority(self):
    package = get_cache()[self.package_name]
    self.assertTrue(
        self.packages.install_priorities.isdisjoint(
            version.priority for version in package.versions))

  def test_installed(self):
    package = get_cache()[self.package_name]
    self.assertTrue(package.is_installed)

  def __str__(self):
    return f'{super().__str__()} {self.package_name}'

  def shortDescription(self):
    version, = get_cache()[self.package_name].versions
    return version.summary


class DependencyTestCase(unittest.TestCase):

  def runTest(self):
    import apt_pkg
    package = get_cache()[self.package_name]
    self.assertTrue(package.is_auto_installed or
                    package._pkg.selected_state == apt_pkg.SELSTATE_DEINSTALL)

  def __str__(self):
    return f'{super().__str__()} {self.package_name}'

  def shortDescription(self):
    version, = get_cache()[self.package_name].versions
    return version.summary


class Call(unittest.mock._Call):

  def __hash__(self):
    if len(self) == 2:
      name = None
      args, kwargs = self
    else:
      name, args, kwargs = self
    return hash((name or None, args, frozenset(kwargs.items())))


unittest.mock._Call = Call


class FilesTestCase(unittest.TestCase):

  @contextlib.contextmanager
  def load_tests(loader, tests, pattern):
    with unittest.mock.patch('builtins.open', side_effect=open) as mock:
      yield iter(
          loader.loadTestsFromTestCase(
              type('FilesTestCase', (FilesTestCase,), dict(mock=mock))))

  def runTest(self):
    a = set(self.mock.call_args_list)
    args = ['git', 'ls-files', 'files']
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
      with io.TextIOWrapper(p.stdout) as f:
        text = f.read()
    b = {unittest.mock.call(filename) for filename in text.splitlines()}
    self.assertEqual(a, b)


class TestSuite(unittest.TestSuite):

  def addTest(self, test):
    if not callable(test):
      test = self.__class__(test)
    else:
      with open('expected-failures') as f:
        if f'{test}\n' in f:
          test = unittest.expectedFailure(test)
      with open('skip') as f:
        if f'{test}\n' in f:
          #test = unittest.skip(None)(test)
          setattr(test, test._testMethodName,
                  unittest.skip(None)(getattr(test, test._testMethodName)))
    super().addTest(test)


class LoadTests:
  registry = []

  def __init__(self, cb):
    self.cb = cb

  def load_tests(self, loader, tests, pattern):
    with FilesTestCase.load_tests(loader, tests, pattern) as result:
      self.cb()
    yield result
    for obj in self.registry:
      yield obj.load_tests(loader, tests, pattern)

  def __call__(self, loader, tests, pattern):
    return TestSuite(self.load_tests(loader, tests, pattern))


def assert_sorted(seq):
  assert seq == sorted(seq)
  return seq


def chain(iterable):
  for elem in iterable:
    yield from elem
