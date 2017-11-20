import fnmatch
import shlex

from preseed import *


class Sed(Sed):

  @property
  def input(self):
    if self.filename == '/target/home/nottheoilrig/.bashrc':
      return '/etc/skel/.bashrc'
    return super().input


class PbuilderPackages(Packages):

  def load_tests(self, loader, tests, pattern):
    for test in super().load_tests(loader, tests, pattern):
      if not any(
          fnmatch.fnmatchcase(f'{test}', pattern)
          for pattern in {
              'test_installed (preseed.PackageTestCase) *',
              'runTest (preseed.DependencyTestCase) *',
          }):
        yield test

  dependency_fields = frozenset([
      'Depends',
      'Pre-Depends',
  ])
  install_priorities = {
      'required',
  }
  man_packages = set()


def preconfiguration_file():
  early_command = CommandSequence([
      Install(open('files/bind_mount'), '/lib/partman/finish.d/', mode='+x'),
      Install(
          open('files/hold-xscreensaver'), '/usr/lib/pre-pkgsel.d/', mode='+x'),
  ])

  # cowbuilder -> dpkg-dev, make
  # elpa-magit -> emacs, git
  # gns3 -> wireshark
  # gnuradio -> python-zmq
  # gqrx-sdr -> gnuradio
  # mitmproxy -> python-mysqldb
  # npm -> libssl-dev
  # python3-matplotlib -> python3-numpy
  # r-base -> libpcre3-dev
  # r-cran-caret -> r-cran-ggplot2
  # r-cran-hmisc -> r-cran-knitr
  packages = Packages(
      chain([
          assert_sorted([
              'apt-file',
              'aptitude',
              'awscli',
              'bison',
              'blueman',
              'byobu',
              'chromium',
              'clang',
              'clang-format',
              'clang-tidy',
              'cmake',
              'cowbuilder',
              'dfu-util',
              'dnsutils',
              'elpa-evil',
              'elpa-expand-region',
              'elpa-fill-column-indicator',
              'elpa-flycheck',
              'elpa-magit',
              'empathy',
              'ess',
              'expect',
              'firmware-iwlwifi',
              'flex',
              'gcc-arm-none-eabi',
              'gdal-bin',
              'gdb',
              'git-email',
              'gitk',
              'gns3',
              'gqrx-sdr',
              'haskell-platform',
              'jekyll',
              'jupyter-console',
              'jupyter-qtconsole',
              'kcachegrind',
              'libclang-dev',
              'libgraph-easy-perl',
              'liblz4-tool',
              'libnotify-bin',
              'lldb',
              'mercurial',
              #'mitmproxy', bug #867250
              'mutt',
              'mypy',
              'nodejs-legacy',
              #'npm', bug #857986
              'octave',
              'pandoc',
              'phantomjs',
              'pylint3',
              'python-mechanize',
              'python-mode',
              'python3-dnspython',
              'python3-flask',
              'python3-fontconfig',
              'python3-gdal',
              'python3-hacking',
              'python3-html5lib',
              'python3-matplotlib',
              'python3-oauth2client',
              'python3-serial',
              'python3-websockets',
              'python3-xcffib',
              'python3-xlsxwriter',
              'qemu',
              'quilt',
              'r-base',
              'r-cran-caret',
              'r-cran-curl',
              'r-cran-e1071',
              'r-cran-gbm',
              'r-cran-hmisc',
              'r-cran-randomforest',
              'r-cran-tikzdevice',
              'r-cran-xml',
              'rr',
              'shellcheck',
              'subversion',
              'suckless-tools',
              'symlinks',
              'tcpdump',
              'telepathy-idle',
              'texlive-xetex',
              'thunderbird',
              'tidy',
              'ubuntu-archive-keyring',
              'vim-gtk3',
              'vim-scripts',
              'vim-syntastic',
              #'vim-youcompleteme', bug #867992
              'vlc',
              'whois',
              'wmctrl',
              #'xfce4-power-manager',
              'xmonad',
              'yapf3',
              'zeal',
          ]),
          chain(
              assert_sorted([
                  assert_sorted([
                      'dsniff',
                      'sslsplit',
                  ]),
                  assert_sorted([
                      'fonts-ipafont',
                      'ttf-dejavu',
                      'ttf-mscorefonts-installer',
                  ]),
                  assert_sorted([
                      'libapache2-mod-php',
                      #'mysql-server', bug #853008
                      'php-mysql',
                  ]),
                  assert_sorted([
                      'libpcre3-dev',
                      'libssl-dev',
                      'python-sphinx',
                      'tcl-dev',
                  ]),
              ])),
          #assert_sorted([
          #    'chromium-dbgsym',
          #    'git-dbgsym',
          #    'libfm-dbg',
          #    'libfm-gtk-dbg',
          #    'libglib2.0-0-dbgsym',
          #    'pcmanfm-dbg',
          #]),
      ]))

  lxde_rc_xml_script = '\n'.join([
      s('<followMouse>.*</followMouse>', '<followMouse>yes</followMouse>'),
      s('<focusDelay>.*</focusDelay>', '<!--&-->'),
      s('Onyx', 'Clearlooks'),
      regexp('</keyboard>') + i('''  <keybind key="M-p">
    <action name="Execute">
      <command>dmenu_run -i</command>
    </action>
  </keybind>
  <keybind key="M-S-g">
    <action name="Execute">
      <command>sh -c {}</command>
    </action>
  </keybind>
  <keybind key="M-S-b">
    <action name="Execute">
      <command>sh -c {}</command>
    </action>
  </keybind>
'''.format(
          shlex.quote(
              r'''wmctrl -F -a "$(wmctrl -l | sed 's/\([^ ]\+ \+\)\{3\}//' | dmenu -i)"'''
          ),
          shlex.quote(
              r'''wmctrl -F -R "$(wmctrl -l | sed 's/\([^ ]\+ \+\)\{3\}//' | dmenu -i)"'''
          ))),
  ])

  zeal = [
      Chdir('/target/home/nottheoilrig/.local/share/Zeal/Zeal/docsets'),
      'wget --no-verbose --output-document - kapeli.com/feeds/CSS.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/Emacs_Lisp.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/Haskell.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/HTML.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/JavaScript.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/MySQL.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/PHP.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/Python_3.tgz | tar xz',
      'wget --no-verbose --output-document - kapeli.com/feeds/Vim.tgz | tar xz',
  ]

  bashrc_script = '\n'.join([
      s('#shopt -s globstar', 'shopt -s globstar'),
      s(r'#\[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"',
        r'[ -x /usr/bin/lesspipe ] \&\& eval "$(SHELL=/bin/sh lesspipe)"'),
      s(r'xterm\*|rxvt\*', 'xterm*|rxvt*|tmux*'),
      regexp('alias grep') + i(r'''    options=" \
      --color \
      --exclude-dir .git \
      --exclude-dir .hg \
      --exclude-dir .svn \
    "'''),
      s(r'#alias \(.\?grep\).*', r'alias \1="\1 $options"'),
      s(r'#\(alias l\)', r'\1'),
      s("alias ll='ls -l'", "alias ll='ls -alF'"),
      regexp('# Alias definitions') +
      i(r'''# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
'''),
      '$' + a(r"""
shopt -s nocaseglob

backup() {
  for filename; do
    'cp' --backup=numbered "$filename" ~/backup/"$(basename "$filename")-$(date +%s)"
  done
}

mkcd() {
  mkdir "$@" && cd "${@: -1}"
}

trash() {
  'mv' --backup=numbered "$@" ~/trash
}

# tmux-256color requires ncurses-term, whereas screen-256color requires
# only ncurses-base.
export BYOBU_COLOR_TERM=tmux-256color

export EMAIL=jack@nottheoilrig.com
export HTML_TIDY=~/.tidy.conf
export LESS=FiRX
export PROMPT_COMMAND="__git_ps1 '${PS1%\\$ }' '$ '"
export SHELLCHECK_OPTS='--exclude SC1090,SC1091,SC2015,SC2016,SC2034,SC2139,SC2148,SC2154,SC2164'"""
             ),
  ])

  ftplugin = [
      #Install('''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/c.vim'),
      #Install('setlocal expandtab',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/config.vim'),
      #Install('''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/cpp.vim'),
      #Install('''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/html.vim'),
      #Install(
      #    '''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #    '/target/home/nottheoilrig/.vim/after/ftplugin/javascript.vim'),
      #Install('''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/json.vim'),
      #Install('''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/lisp.vim'),
      Install(r'''setlocal
  \ expandtab
  \ shiftwidth=2
  \ softtabstop=-1''',
              '/target/home/nottheoilrig/.vim/after/ftplugin/markdown.vim'),
      Install(r'''setlocal
  \ shiftwidth=2
  \ softtabstop=-1''',
              '/target/home/nottheoilrig/.vim/after/ftplugin/python.vim'),
      #Install('setlocal shiftwidth=2',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/r.vim'),
      Install(r'''setlocal
  \ expandtab
  \ shiftwidth=2
  \ softtabstop=-1''', '/target/home/nottheoilrig/.vim/after/ftplugin/sh.vim'),
      Install(r'''setlocal
  \ expandtab
  \ shiftwidth=2
  \ softtabstop=-1''', '/target/home/nottheoilrig/.vim/after/ftplugin/vim.vim'),
      #Install('''setlocal softtabstop=-1
      #setlocal shiftwidth=2''',
      #        '/target/home/nottheoilrig/.vim/after/ftplugin/yaml.vim'),
  ]

  pbuilder = [
      Install(open('files/G00'), '/target/home/nottheoilrig/hooks/', mode='+x'),
      Install(
          open('files/B90lintian'),
          '/target/home/nottheoilrig/hooks/',
          mode='+x'),
      Append(
          r'''
EATMYDATA=yes
CCACHEDIR=/var/cache/pbuilder/ccache
DISTRIBUTION=testing
HOOKDIR=~nottheoilrig/hooks
OTHERMIRROR='deb http://debug.mirrors.debian.org/debian-debug testing-debug main'
EXTRAPACKAGES=" \
  {} \
"'''.format(' \\\n  '.join(
              # intltool -> automake
              PbuilderPackages(
                  assert_sorted([
                      'autopoint',
                      'bison',
                      'flex',
                      'git',
                      'gperf',
                      'intltool',
                      'less',
                      'libtool',
                      'man-db',
                      'mercurial',
                      'valac',
                      'vim',
                      'wget',
                  ])))),
          '/target/etc/pbuilderrc'),
      'in-target cowbuilder create',
  ]

  late_command = CommandSequence([
      Copy('/target/etc/xdg/lxsession/LXDE/desktop.conf',
           '/target/home/nottheoilrig/.config/lxsession/LXDE/'),
      Sed(
          s('sNet/IconThemeName=.*', 'sNet/IconThemeName=Adwaita'),
          '/target/home/nottheoilrig/.config/lxsession/LXDE/desktop.conf'),
      #Copy(
      #    '/target/etc/xdg/autostart/notification-daemon-autostart.desktop',
      #    '/target/home/nottheoilrig/.config/autostart/'),
      #Sed(
      #    s('OnlyShowIn=.*', '&LXDE;'),
      #    '/target/home/nottheoilrig/.config/autostart/notification-daemon-autostart.desktop'
      #),
      Copy('/target/etc/xdg/openbox/LXDE/rc.xml',
           '/target/home/nottheoilrig/.config/openbox/lxde-rc.xml'),
      Sed(lxde_rc_xml_script,
          '/target/home/nottheoilrig/.config/openbox/lxde-rc.xml'),
      Install(
          open('files/autostart'),
          '/target/home/nottheoilrig/.config/openbox/'),
      Install(
          open('files/mimeapps.list'), '/target/home/nottheoilrig/.config/'),
      Copy('/target/etc/xdg/lxpanel/LXDE/panels/panel',
           '/target/home/nottheoilrig/.config/lxpanel/LXDE/panels/'),
      Sed('\n'.join([
          s('usefontcolor=.*', 'usefontcolor=0'),
          s('background=.*', 'background=0'),
      ]), '/target/home/nottheoilrig/.config/lxpanel/LXDE/panels/panel'),
      #Install(
      #    open('files/clipitrc'),
      #    '/target/home/nottheoilrig/.config/clipit/'),
      Install(
          open('files/lxterminal.conf'),
          '/target/home/nottheoilrig/.config/lxterminal/'),
      #Copy(
      #    '/target/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml',
      #    '/target/home/nottheoilrig/.config/xfce4/xfconf/xfce-perchannel-xml/'
      #),
      #r'''echo -e '\#<property .*/># d;\#</property># i \\\n    <property name="show-tray-icon" type="int" value="1"/>\\\n    <property name="sleep-button-action" type="uint" value="1"/>\\\n    <property name="hibernate-button-action" type="uint" value="2"/>\\\n    <property name="critical-power-action" type="uint" value="2"/>' | sed --file - --in-place /target/home/nottheoilrig/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml''',
      'in-target su nottheoilrig --command ' +
      shlex.quote('byobu-ctrl-a screen'),
      'in-target su nottheoilrig --command ' + shlex.quote('byobu-keybindings'),
      Install(
          open('files/tmux.conf'),
          '/target/home/nottheoilrig/.config/byobu/.tmux.conf'),
      Install(open('files/style'), '/target/home/nottheoilrig/.config/yapf/'),
      Install(open('files/flake8'), '/target/home/nottheoilrig/.config/'),
      Install(
          open('files/accounts.cfg'),
          '/target/home/nottheoilrig/.local/share/telepathy/mission-control/'),
      *zeal,
      #
      Install(open('files/xmonad.hs'), '/target/home/nottheoilrig/.xmonad/'),
      'XDG_CONFIG_HOME=/home/nottheoilrig/.config in-target su nottheoilrig --command '
      + shlex.quote('byobu-enable'),
      Sed(bashrc_script, '/target/home/nottheoilrig/.bashrc'),
      Install(
          open('files/bash_aliases'),
          '/target/home/nottheoilrig/.bash_aliases'),
      Install(open('files/inputrc'), '/target/home/nottheoilrig/.inputrc'),
      Install(open('files/vimrc'), '/target/home/nottheoilrig/.vimrc'),
      *ftplugin,
      'in-target su nottheoilrig --command ' +
      shlex.quote(r'''vim-addons install \
    nerd-commenter \
    youcompleteme \
  '''),
      Install(open('files/emacs'), '/target/home/nottheoilrig/.emacs'),
      '> /target/home/nottheoilrig/.selected_editor',
      'chown 1000:1000 /target/home/nottheoilrig/.selected_editor',
      #'cd /target/home/nottheoilrig',
      #'wget --no-verbose --output-document - cdist2.perforce.com/perforce/r15.2/bin.linux26x86_64/p4v.tgz | tar xz',
      #'chown --recursive 1000:1000 /target/home/nottheoilrig/p4v-2015.2.1458499',
      'in-target su nottheoilrig --command ' +
      shlex.quote('git config --global branch.autoSetupRebase always'),
      'in-target su nottheoilrig --command ' +
      shlex.quote('git config --global pager.status true'),
      'in-target su nottheoilrig --command ' + shlex.quote(
          "git config --global pager.log 'perl /usr/share/doc/git/contrib/diff-highlight/diff-highlight | less'"
      ),
      'in-target su nottheoilrig --command ' + shlex.quote(
          "git config --global pager.show 'perl /usr/share/doc/git/contrib/diff-highlight/diff-highlight | less'"
      ),
      'in-target su nottheoilrig --command ' + shlex.quote(
          "git config --global pager.diff 'perl /usr/share/doc/git/contrib/diff-highlight/diff-highlight | less'"
      ),
      'in-target su nottheoilrig --command ' + shlex.quote(
          "git config --global interactive.diffFilter 'perl /usr/share/doc/git/contrib/diff-highlight/diff-highlight'"
      ),
      #'in-target su nottheoilrig --command ' + shlex.quote('git config --global diff.compactionHeuristic true'),
      'in-target su nottheoilrig --command ' +
      shlex.quote('git config --global credentials.helper store'),
      #'> /target/home/nottheoilrig/.git-credentials',
      #'chown 1000:1000 /target/home/nottheoilrig/.git-credentials',
      #'wget --no-verbose --output-document /target/home/nottheoilrig/.hgrc nottheoilrig.com/d-i/hgrc',
      #'chown 1000:1000 /target/home/nottheoilrig/.hgrc',
      Install(open('files/gdbinit'), '/target/home/nottheoilrig/.gdbinit'),
      Install(open('files/pylintrc'), '/target/home/nottheoilrig/.pylintrc'),
      Install(open('files/credentials'), '/target/home/nottheoilrig/.aws/'),
      Install(open('files/muttrc'), '/target/home/nottheoilrig/.muttrc'),
      Install(
          open('files/aspell.conf'), '/target/home/nottheoilrig/.aspell.conf'),
      'cd /tmp',
      'wget --no-verbose languagetool.org/download/LanguageTool-stable.zip',
      'unzip -d /target/home/nottheoilrig /tmp/LanguageTool-stable',
      'chown --recursive 1000:1000 /target/home/nottheoilrig/LanguageTool-3.9',
      'cd /target/home/nottheoilrig',
      'in-target su nottheoilrig --command ' + shlex.quote(
          'git clone https://github.com/mhayashi1120/Emacs-langtool.git'),
      #
      *pbuilder,
      #
      Sed(
          regexp(r'\.ifdef REMOTE_SMTP_SMARTHOST_HOSTS_AVOID_TLS') +
          i('  protocol = smtps'), '/target/etc/exim4/exim4.conf.template'),
      Append('*:nottheoilrig:', '/target/etc/exim4/passwd.client'),
      'in-target adduser nottheoilrig dialout',
      'in-target adduser nottheoilrig wireshark',
      'in-target a2enmod userdir',
      Sed(
          s('XKBOPTIONS=""', 'XKBOPTIONS="ctrl:nocaps"'),
          '/target/etc/default/keyboard'),
  ])

  return PreconfigurationFile([
      ('d-i', 'debian-installer/language', 'string', 'en'),
      ('d-i', 'debian-installer/country', 'string', 'CA'),
      ('d-i', 'keyboard-configuration/xkb-keymap', 'select', 'us'),
      ('d-i', 'mirror/country', 'string', 'manual'),
      ('d-i', 'mirror/http/hostname', 'string', 'debian.osuosl.org'),
      ('d-i', 'mirror/http/directory', 'string', '/debian'),
      ('d-i', 'mirror/suite', 'string', 'testing'),
      ('d-i', 'passwd/root-login', 'boolean', 'false'),
      ('d-i', 'passwd/user-fullname', 'string', 'Jack Bates'),
      ('d-i', 'passwd/username', 'string', 'nottheoilrig'),
      ('d-i', 'time/zone', 'string', 'America/Creston'),
      #
      ('d-i', 'partman/early_command', 'string', early_command),
      #
      ('d-i', 'apt-setup/non-free', 'boolean', 'true'),
      ('d-i', 'apt-setup/local0/repository', 'string',
       'http://debug.mirrors.debian.org/debian-debug testing-debug main'),
      ('tasksel', 'tasksel/desktop', 'string', 'lxde'),
      ('d-i', 'pkgsel/include', 'string', packages),
      #
      ('d-i', 'grub-installer/bootdev', 'string', 'default'),
      #
      ('d-i', 'preseed/late_command', 'string', late_command),
      #
      ('exim4-config', 'exim4/dc_eximconfig_configtype', 'select',
       'mail sent by smarthost; received via SMTP or fetchmail'),
      ('exim4-config', 'exim4/dc_smarthost', 'string', 'mail.nottheoilrig.com'),
      ('wireshark-common', 'wireshark-common/install-setuid', 'boolean',
       'true'),
  ])


if __name__ == '__main__':
  print(preconfiguration_file())

load_tests = LoadTests(preconfiguration_file)
