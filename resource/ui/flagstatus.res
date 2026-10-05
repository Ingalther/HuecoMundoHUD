// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).
"Resource/UI/FlagStatus.res"
{
	"Arrow"
	{
		"ControlName"		"CTFArrowPanel"
		"fieldName"		"Arrow"
		"xpos"		"52"
		"ypos"		"0"
		"zpos"		"1"
		"wide"		"56"
		"tall"		"56"
		"visible"		"1"
		"enabled"		"1"
		"scaleImage"		"1"
	}
	"Briefcase"
	{
		"ControlName"		"CTFImagePanel"
		"fieldName"		"Briefcase"
		"xpos"		"66"
		"ypos"		"14"
		"zpos"		"2"
		"wide"		"28"
		"tall"		"28"
		"visible"		"1"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_briefcase"
		"scaleImage"		"1"
		"if_mvm"
		{
			"xpos"		"64"
			"ypos"		"12"
			"wide"		"32"
			"tall"		"32"
		}
	}
	"StatusIcon"
	{
		"ControlName"		"CTFImagePanel"
		"fieldName"		"StatusIcon"
		"xpos"		"69"
		"ypos"		"17"
		"zpos"		"3"
		"wide"		"22"
		"tall"		"22"
		"visible"		"1"
		"enabled"		"1"
		"image"		"../hud/objectives_flagpanel_ico_flag_home"
		"scaleImage"		"1"
		"if_mvm"
		{
			"visible"		"0"
		}
	}
}
