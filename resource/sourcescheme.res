// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).
#base "SourceSchemeBase.res"
"Scheme"
{
	"Colors"
	{
		"TFDarkBrown"		"52 53 53 255"
		"TFDarkBrownTransparent"		"52 53 53 190"
		"TFTanBright"		"209 210 210 150"
		"TFTanLight"		"174 175 175 150"
		"TFTanMedium"		"112 113 113 150"
		"TFTanLightBright"		"205 206 206 90"
		"TFTanLightDark"		"83 84 84 90"
		"TFOrangeBright"		"34 156 102 255"
		"TFTextBright"		"218 219 219 150"
		"TFTextLight"		"174 175 175 255"
		"TFTextMedium"		"112 113 113 255"
		"TFTextMediumDark"		"89 90 90 255"
		"TFTextBlack"		"37 38 38 255"
		"TFTextDull"		"112 113 113 255"
		"TFMediumBrown"		"60 61 61 255"
		"QuickListBGDeselected"		"60 61 61 255"
		"QuickListBGSelected"		"112 113 113 150"
		"Blank"		"0 0 0 0"
		"ControlBG"		"76 88 68 255"
		"ControlDarkBG"		"90 106 80 255"
		"WindowBG"		"62 70 55 255"
		"SelectionBG"		"78 79 79 255"
		"SelectionBG2"		"60 61 61 255"
		"ListBG"		"34 35 35 255"
	}
	"BaseSettings"
	{
		"Border.Bright"		"TFTanLightDark"
		"Border.Dark"		"TFTanLightDark"
		"Border.Selection"		"BorderSelection"
		"Button.TextColor"		"TFDarkBrown"
		"Button.BgColor"		"TFTanLight"
		"Button.ArmedTextColor"		"TFDarkBrown"
		"Button.ArmedBgColor"		"TFTanBright"
		"Button.DepressedTextColor"		"TFDarkBrown"
		"Button.DepressedBgColor"		"TFTanLight"
		"Button.FocusBorderColor"		"TransparentBlack"
		"CheckButton.TextColor"		"TFTextBright"
		"CheckButton.SelectedTextColor"		"TFTextBright"
		"CheckButton.BgColor"		"ListBG"
		"CheckButton.HighlightFgColor"		"TFTextMedium"
		"CheckButton.ArmedBgColor"		"Blank"
		"CheckButton.DepressedBgColor"		"Blank"
		"CheckButton.Border1"		"Border.Dark"
		"CheckButton.Border2"		"Border.Bright"
		"CheckButton.Check"		"TFTanBright"
		"CheckButton.DisabledBgColor"		"ListBG"
		"ToggleButton.SelectedTextColor"		"TFTextBright"
		"ComboBoxButton.ArrowColor"		"TFTanLight"
		"ComboBoxButton.ArmedArrowColor"		"TFTanBright"
		"ComboBoxButton.BgColor"		"Blank"
		"ComboBoxButton.DisabledBgColor"		"Blank"
		"RadioButton.TextColor"		"TFTextBright"
		"RadioButton.SelectedTextColor"		"TFTextBright"
		"RadioButton.ArmedTextColor"		"TFTextMedium"
		"Frame.BgColor"		"TFDarkBrown"
		"Frame.OutOfFocusBgColor"		"TFDarkBrownTransparent"
		"FrameGrip.Color1"		"TFTanMedium"
		"FrameGrip.Color2"		"TFDarkBrown"
		"FrameTitleButton.FgColor"		"TFTanBright"
		"FrameTitleBar.Font"		"DefaultLarge" [!$OSX]
		"FrameTitleBar.TextColor"		"TFTanBright"
		"FrameTitleBar.DisabledTextColor"		"TFTanLight"
		"Label.TextDullColor"		"TFTextDull"
		"Label.TextColor"		"TFTextBright"
		"Label.TextBrightColor"		"TFTextBright"
		"Label.SelectedTextColor"		"TFTextBright"
		"Label.BgColor"		"Blank"
		"Label.DisabledFgColor1"		"TFTextDull"
		"Label.DisabledFgColor2"		"Blank"
		"ListPanel.TextColor"		"TFTextBright"
		"ListPanel.BgColor"		"ListBG"
		"ListPanel.SelectedBgColor"		"SelectionBG"
		"ListPanel.SelectedOutOfFocusBgColor"		"SelectionBG2"
		"MainMenu.TextColor"		"TanLight" [!$OSX]
		"MainMenu.ArmedTextColor"		"100 101 101 255" [!$OSX]
		"MainMenu.Inset"		"32"
		"Menu.TextInset"		"6"
		"Menu.FgColor"		"TFTextLight"
		"Menu.BgColor"		"ListBG"
		"Menu.ArmedFgColor"		"TFTextBright"
		"Menu.ArmedBgColor"		"TFOrangeBright"
		"Menu.DividerColor"		"BorderDark"
		"ScrollBarButton.FgColor"		"TFDarkBrown"
		"ScrollBarButton.BgColor"		"TFTanLight"
		"ScrollBarButton.ArmedFgColor"		"TFDarkBrown"
		"ScrollBarButton.ArmedBgColor"		"TFTanBright"
		"ScrollBarButton.DepressedFgColor"		"TFDarkBrown"
		"ScrollBarButton.DepressedBgColor"		"TFTanLight"
		"ScrollBarSlider.BgColor"		"TFTanMedium"
		"ScrollBarSlider.FgColor"		"TFTanLight"
		"Slider.NobColor"		"TFTanLight"
		"Slider.TextColor"		"TFTextBright"
		"Slider.TrackColor"		"ListBG"
		"Slider.DisabledTextColor1"		"TFTextMediumDark"
		"Slider.DisabledTextColor2"		"Blank"
		"TextEntry.TextColor"		"TFTextBright"
		"TextEntry.DisabledTextColor"		"TFTextMedium"
		"TextEntry.SelectedBgColor"		"TFOrangeBright"
	}
	"Fonts"
	{
		"MainMenuFont"
		{
			"1" [!$OSX]
			{
				"name"		"TF2 Build"
				"tall"		"18"
				"weight"		"500"
				"additive"		"0"
				"antialias"		"1"
			}
		}
		"MenuLarge"
		{
			"1" [$X360]
			{
				"tall_hidef"		"24"
			}
		}
		"ServerBrowserTitle"
		{
			"1"
			{
				"name"		"TF2 Build"
				"tall"		"35"
				"tall_lodef"		"40"
				"weight"		"500"
				"additive"		"0"
				"antialias"		"1"
			}
		}
		"Default" [$OSX]
		{
			"1"
			{
				"name"		"Verdana"
				"tall"		"14"
				"weight"		"500"
			}
		}
		"ServerBrowserSmall"
		{
			"1"
			{
				"name"		"Tahoma"
				"tall"		"16"
				"weight"		"0"
				"range"		"0x0000 0x017F"
				"yres"		"480 599"
			}
			"2"
			{
				"name"		"Tahoma"
				"tall"		"16"
				"weight"		"0"
				"range"		"0x0000 0x017F"
				"yres"		"600 767"
			}
			"3"
			{
				"name"		"Tahoma"
				"tall"		"16"
				"weight"		"0"
				"range"		"0x0000 0x017F"
				"yres"		"768 1023"
				"antialias"		"1"
			}
			"4"
			{
				"name"		"Tahoma"
				"tall"		"19"
				"weight"		"0"
				"range"		"0x0000 0x017F"
				"yres"		"1024 1199"
				"antialias"		"1"
			}
			"5"
			{
				"name"		"Tahoma"
				"tall"		"19"
				"weight"		"0"
				"range"		"0x0000 0x017F"
				"yres"		"1200 6000"
				"antialias"		"1"
			}
		}
		"AchievementItemTitle" [!$OSX]
		{
			"1"
			{
				"name"		"Arial" [!$OSX]
				"name"		"Verdana Bold" [$OSX]
				"weight"		"1500"
				"tall"		"16" [!$OSX]
				"tall"		"18" [$OSX]
				"antialias"		"1"
			}
		}
		"AchievementItemTitleLarge" [!$OSX]
		{
			"1"
			{
				"name"		"Arial" [!$OSX]
				"name"		"Verdana Bold" [$OSX]
				"weight"		"1500"
				"tall"		"18" [!$OSX]
				"tall"		"19" [$OSX]
				"antialias"		"1"
			}
		}
		"AchievementItemDescription" [!$OSX]
		{
			"1"
			{
				"name"		"Arial" [!$OSX]
				"name"		"Verdana" [$OSX]
				"weight"		"1000"
				"tall"		"14" [!$OSX]
				"tall"		"12" [$OSX]
				"antialias"		"1" [!$OSX]
			}
		}
	}
	"CustomFontFiles"
	{
		"6"
		{
			"font"		"resource/TF2Build.ttf"
			"name"		"TF2 Build"
			"turkish"
			{
				"range"		"0x0000 0x015F"
			}
			"swedish"
			{
				"range"		"0x0000 0x00F6"
			}
			"spanish"
			{
				"range"		"0x0000 0x00FC"
			}
			"romanian"
			{
				"range"		"0x0000 0x021B"
			}
			"polish"
			{
				"range"		"0x0000 0x017C"
			}
			"norwegian"
			{
				"range"		"0x0000 0x00F8"
			}
			"danish"
			{
				"range"		"0x0000 0x00F8"
			}
			"hungarian"
			{
				"range"		"0x0000 0x0171"
			}
			"german"
			{
				"range"		"0x0000 0x00FC"
			}
			"french"
			{
				"range"		"0x0000 0x0178"
			}
			"finnish"
			{
				"range"		"0x0000 0x017E"
			}
			"czech"
			{
				"range"		"0x0000 0x017E"
			}
			"bulgarian"
			{
				"range"		"0x0000 0x0451"
			}
			"russian"
			{
				"range"		"0x0000 0x0451"
			}
		}
		"10"		"resource/linux_fonts/DejaVuSans.ttf"
		"11"		"resource/linux_fonts/DejaVuSans-Bold.ttf"
		"12"		"resource/linux_fonts/DejaVuSans-BoldOblique.ttf"
		"13"		"resource/linux_fonts/DejaVuSans-Oblique.ttf"
		"14"		"resource/linux_fonts/LiberationSans-Regular.ttf"
		"15"		"resource/linux_fonts/LiberationSans-Bold.ttf"
		"16"		"resource/linux_fonts/LiberationMono-Regular.ttf"
		"17"		"resource/linux_fonts/FiraSans-Regular.ttf"
	}
}
