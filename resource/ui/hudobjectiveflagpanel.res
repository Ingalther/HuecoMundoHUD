// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).
"Resource/UI/HudObjectiveFlagPanel.res"
{
	"ObjectiveStatusFlagPanel"
	{
		"ControlName"		"EditablePanel"
		"fieldName"		"ObjectiveStatusFlagPanel"
		"xpos"		"0"
		"ypos"		"0"
		"zpos"		"1"
		"wide"		"f0"
		"tall"		"480"
		"visible"		"1"
		"enabled"		"1"
		"if_hybrid"
		{
			"zpos"		"-1"
		}
	}
	"LeftSideBG"
	{
		"ControlName"		"ImagePanel"
		"fieldName"		"LeftSideBG"
		"xpos"		"c-90"
		"ypos"		"r48"
		"zpos"		"1"
		"wide"		"180"
		"tall"		"39"
		"visible"		"1"
		"enabled"		"1"
		"image"		"replay/thumbnails/hm/ctf_bar"
		"scaleImage"		"1"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"RightSideBG"
	{
		"ControlName"		"ImagePanel"
		"fieldName"		"RightSideBG"
		"xpos"		"c-140"
		"ypos"		"r75" [$WIN32]
		"ypos"		"r96" [$X360]
		"zpos"		"1"
		"wide"		"0"
		"tall"		"0"
		"visible"		"0"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_bg_right"
		"scaleImage"		"1"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"OutlineBG"
	{
		"ControlName"		"ImagePanel"
		"fieldName"		"OutlineBG"
		"xpos"		"c-140"
		"ypos"		"r75" [$WIN32]
		"ypos"		"r96" [$X360]
		"zpos"		"2"
		"wide"		"0"
		"tall"		"0"
		"visible"		"0"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_bg_outline"
		"scaleImage"		"1"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"BlueScore"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"BlueScore"
		"xpos"		"c-80"
		"ypos"		"r47"
		"zpos"		"8"
		"wide"		"60"
		"tall"		"36"
		"visible"		"1"
		"enabled"		"1"
		"textAlignment"		"center"
		"labelText"		"%bluescore%"
		"font"		"HM_Streak"
		"fgcolor"		"HM_Bone"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"BlueScoreShadow"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"BlueScoreShadow"
		"xpos"		"c-79"
		"ypos"		"r46"
		"zpos"		"7"
		"wide"		"60"
		"tall"		"36"
		"visible"		"1"
		"enabled"		"1"
		"textAlignment"		"center"
		"labelText"		"%bluescore%"
		"font"		"HM_Streak"
		"fgcolor"		"HM_Shadow"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"RedScore"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"RedScore"
		"xpos"		"c20"
		"ypos"		"r47"
		"zpos"		"8"
		"wide"		"60"
		"tall"		"36"
		"visible"		"1"
		"enabled"		"1"
		"textAlignment"		"center"
		"labelText"		"%redscore%"
		"font"		"HM_Streak"
		"fgcolor"		"HM_Bone"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"RedScoreShadow"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"RedScoreShadow"
		"xpos"		"c21"
		"ypos"		"r46"
		"zpos"		"7"
		"wide"		"60"
		"tall"		"36"
		"visible"		"1"
		"enabled"		"1"
		"textAlignment"		"center"
		"labelText"		"%redscore%"
		"font"		"HM_Streak"
		"fgcolor"		"HM_Shadow"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"OutlineImage"
	{
		"ControlName"		"CTFImagePanel"
		"fieldName"		"OutlineImage"
		"xpos"		"c-50"
		"ypos"		"r127" [$WIN32]
		"ypos"		"r148" [$X360]
		"zpos"		"9"
		"wide"		"0"
		"tall"		"0"
		"visible"		"0"
		"enabled"		"1"
		"image"		"replay/thumbnails/hm/blank"
		"scaleImage"		"1"
	}
	"CarriedImage"
	{
		"ControlName"		"ImagePanel"
		"fieldName"		"CarriedImage"
		"xpos"		"c168"
		"ypos"		"r44"
		"zpos"		"10"
		"wide"		"28"
		"tall"		"28"
		"visible"		"0"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_carried_red"
		"scaleImage"		"1"
	}
	"PlayingTo"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"PlayingTo"
		"xpos"		"c-70"
		"ypos"		"r12"
		"zpos"		"4"
		"wide"		"140"
		"tall"		"12"
		"visible"		"1"
		"enabled"		"1"
		"labelText"		"#TF_PlayingTo"
		"textAlignment"		"center"
		"dulltext"		"0"
		"brighttext"		"0"
		"font"		"HM_Small"
		"fgcolor"		"HM_Ash"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"PlayingToBG"
	{
		"ControlName"		"CTFImagePanel"
		"fieldName"		"PlayingToBG"
		"xpos"		"c-75" [$WIN32]
		"xpos"		"c-70" [$X360]
		"ypos"		"r31" [$WIN32]
		"ypos"		"r51" [$X360]
		"zpos"		"3"
		"wide"		"0"
		"tall"		"0"
		"visible"		"0"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_bg_playingto"
		"image_hidef"		"../hud/objectives_flagpanel_bg_playingto_hidef"
		"scaleImage"		"1"
		"if_hybrid"
		{
			"visible"		"0"
		}
		"if_mvm"
		{
			"visible"		"0"
		}
		"if_specialdelivery"
		{
			"visible"		"0"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"BlueFlag"
	{
		"ControlName"		"CTFFlagStatus"
		"fieldName"		"BlueFlag"
		"xpos"		"c-202"
		"ypos"		"r58"
		"zpos"		"5"
		"wide"		"160"
		"tall"		"90"
		"visible"		"1"
		"enabled"		"1"
		"if_hybrid"
		{
			"visible"		"0"
			"ypos"		"r100"
		}
		"if_hybrid_single"
		{
			"xpos"		"c-80"
		}
		"if_hybrid_double"
		{
			"xpos"		"c-115"
		}
		"if_specialdelivery"
		{
			"ypos"		"r100"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"RedFlag"
	{
		"ControlName"		"CTFFlagStatus"
		"fieldName"		"RedFlag"
		"xpos"		"c42"
		"ypos"		"r58"
		"zpos"		"5"
		"wide"		"160"
		"tall"		"90"
		"visible"		"1"
		"enabled"		"1"
		"if_hybrid"
		{
			"visible"		"0"
			"ypos"		"r100"
		}
		"if_hybrid_single"
		{
			"xpos"		"c-80"
		}
		"if_hybrid_double"
		{
			"xpos"		"c-45"
		}
		"if_specialdelivery"
		{
			"ypos"		"r100"
		}
		"if_no_flags"
		{
			"visible"		"0"
		}
	}
	"CaptureFlag"
	{
		"ControlName"		"CTFArrowPanel"
		"fieldName"		"CaptureFlag"
		"xpos"		"c154"
		"ypos"		"r58"
		"zpos"		"5"
		"wide"		"56"
		"tall"		"56"
		"visible"		"0"
		"enabled"		"1"
	}
	"PoisonIcon"
	{
		"ControlName"		"ImagePanel"
		"fieldName"		"PoisonIcon"
		"xpos"		"cs-0.5"
		"ypos"		"r75"
		"zpos"		"6"
		"wide"		"40"
		"tall"		"o1"
		"visible"		"0"
		"enabled"		"1"
		"image"		"marked_for_death"
		"scaleImage"		"1"
	}
	"PoisonTimeLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"PoisonTimeLabel"
		"xpos"		"cs-0.5"
		"ypos"		"r65"
		"zpos"		"6"
		"wide"		"40"
		"tall"		"20"
		"visible"		"0"
		"enabled"		"1"
		"textAlignment"		"center"
		"labelText"		"%redscore%"
		"font"		"HudFontMediumBold"
		"fgcolor"		"TanLight"
	}
	"SpecCarriedImage"
	{
		"ControlName"		"ImagePanel"
		"fieldName"		"SpecCarriedImage"
		"xpos"		"c168"
		"ypos"		"r44"
		"zpos"		"10"
		"wide"		"28"
		"tall"		"28"
		"visible"		"0"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_carried_red"
		"scaleImage"		"1"
	}
}
