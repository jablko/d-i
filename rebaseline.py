import unittest

if __name__ == '__main__':
  loader = unittest.defaultTestLoader
  runner = unittest.TextTestRunner(resultclass=unittest.TestResult)
  result = runner.run(loader.discover('.'))
  with open('expected-failures', 'a+') as f:
    f.seek(0)
    text = f.read()
    f.truncate(0)
    print(
        '\n'.join(
            set(text.splitlines()).intersection(
                f'{test}' for test, err in result.expectedFailures).union(
                    f'{test}' for test, err in result.failures)),
        file=f)
  with open('skip', 'a+') as f:
    f.seek(0)
    text = f.read()
    f.truncate(0)
    print(
        '\n'.join(
            set(text.splitlines()).intersection(
                f'{test}' for test, reason in result.skipped).union(
                    f'{test}' for test, err in result.errors)),
        file=f)
