import XMonad
import XMonad.Config.Desktop
import XMonad.Hooks.EwmhDesktops
import XMonad.Layout.NoBorders
import XMonad.Util.EZConfig
import XMonad.Actions.WindowBringer
import XMonad.Layout.LimitWindows
import XMonad.Actions.UpdatePointer

main = xmonad
  $ desktopConfig
  { layoutHook = limitSelect 1 1
    $ smartBorders
    $ layoutHook desktopConfig
  , logHook = logHook desktopConfig
    >> updatePointer (0.5, 0.5) (1, 1)
  , handleEventHook = handleEventHook desktopConfig
    <+> fullscreenEventHook
  }
  `additionalKeysP`
  [ ("M-S-g", gotoMenu)
  , ("M-S-b", bringMenu)
  , ("M-S-,", increaseLimit)
  , ("M-S-.", decreaseLimit)
  ]
