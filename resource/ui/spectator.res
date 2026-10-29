// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).
"Resource/UI/Spectator.res"
{
	"Spectator"
	{
		"ControlName"		"Frame"
		"fieldName"		"Spectator"
		"tall"		"480"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
	}
	"specgui"
	{
	}
	"topbar"
	{
		"ControlName"		"Panel"
		"fieldName"		"TopBar"
		"xpos"		"0"
		"ypos"		"0"
		"tall"		"0"
		"wide"		"f0"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"0"
		"enabled"		"1"
		"tabPosition"		"0"
	}
	"BottomBar"
	{
		"ControlName"		"Frame"
		"fieldName"		"BottomBar"
		"xpos"		"0"
		"ypos"		"9999"
		"tall"		"0"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"0"
		"enabled"		"0"
		"tabPosition"		"0"
		"wide"		"0"
	}
	"bottombarblank"
	{
		"ControlName"		"Panel"
		"fieldName"		"bottombarblank"
		"xpos"		"0"
		"ypos"		"r0"
		"tall"		"0"
		"wide"		"f0"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"0"
		"enabled"		"1"
		"tabPosition"		"0"
	}
	"ReinforcementsLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"ReinforcementsLabel"
		"xpos"		"c-160"
		"ypos"		"37"
		"wide"		"320"
		"tall"		"29"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"labelText"		"#game_respawntime_in_secs"
		"textAlignment"		"center"
		"font"		"HM_NoticeTitle"
		"zpos"		"2"
		"fgcolor_override"		"HM_Bone"
		"paintbackground"		"0"
		"paintborder"		"1"
		"border"		"HM_RespawnCard"
	}
	"BuyBackLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"BuyBackLabel"
		"xpos"		"0"
		"ypos"		"0"
		"wide"		"400"
		"tall"		"f0"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"0"
		"enabled"		"1"
		"labelText"		""
		"textAlignment"		"center"
		"font"		"HudFontSmall"
		"wrap"		"1"
		"centerwrap"		"1"
	}
	"MapLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"MapLabel"
		"font"		"HM_SpecMap"
		"xpos"		"r260" [$WIN32]
		"ypos"		"16" [$WIN32]
		"xpos"		"r285" [$X360]
		"ypos"		"32" [$X360]
		"wide"		"240" [$WIN32]
		"wide"		"220" [$X360]
		"tall"		"20"
		"tall_hidef"		"30"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"labelText"		"map: cp_bridge"
		"textAlignment"		"east"
	}
	"ClassOrTeamLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"ClassOrTeamLabel"
		"xpos"		"c-85"
		"xpos_hidef"		"c-65"
		"xpos_lodef"		"40"
		"ypos"		"68"
		"ypos_hidef"		"90"
		"ypos_lodef"		"30"
		"wide"		"170"
		"wide_hidef"		"130"
		"wide_lodef"		"220"
		"tall"		"15"
		"tall_lodef"		"25"
		"zpos"		"2"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_ChangeTeam"
		"textAlignment"		"center"
		"textAlignment_lodef"		"north-west"
		"font"		"HM_SpecHint"
		"wrap_lodef"		"1"
	}
	"SwitchCamModeKeyLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"SwitchCamModeKeyLabel"
		"xpos"		"5" [$WIN32]
		"ypos"		"r110"
		"xpos"		"53" [$X360]
		"wide"		"60" [$WIN32]
		"wide"		"60" [$X360]
		"tall"		"20"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_ChangeTeam"
		"textAlignment"		"east"
		"font"		"HM_SpecHint"
	}
	"SwitchCamModeLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"SwitchCamModeLabel"
		"xpos"		"80" [$WIN32]
		"ypos"		"r110"
		"xpos"		"128" [$X360]
		"wide"		"125" [$WIN32]
		"wide"		"95" [$X360]
		"tall"		"20"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_SwitchCamMode"
		"textAlignment"		"west"
		"font"		"HM_SpecHint"
	}
	"CycleTargetFwdKeyLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"CycleTargetFwdKeyLabel"
		"xpos"		"5" [$WIN32]
		"ypos"		"r100"
		"xpos"		"53" [$X360]
		"wide"		"60" [$WIN32]
		"wide"		"60" [$X360]
		"tall"		"20"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_ClassOrTeamKey"
		"textAlignment"		"east"
		"font"		"HM_SpecHint"
	}
	"CycleTargetFwdLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"CycleTargetFwdLabel"
		"xpos"		"80" [$WIN32]
		"ypos"		"r100"
		"xpos"		"128" [$X360]
		"wide"		"125" [$WIN32]
		"wide"		"95" [$X360]
		"tall"		"20"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_CycleTargetFwd"
		"textAlignment"		"west"
		"font"		"HM_SpecHint"
	}
	"CycleTargetRevKeyLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"CycleTargetRevKeyLabel"
		"xpos"		"5" [$WIN32]
		"ypos"		"r90"
		"xpos"		"53" [$X360]
		"wide"		"60" [$WIN32]
		"wide"		"60" [$X360]
		"tall"		"20"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_ClassOrTeamKey"
		"textAlignment"		"east"
		"font"		"HM_SpecHint"
	}
	"CycleTargetRevLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"CycleTargetRevLabel"
		"xpos"		"80" [$WIN32]
		"ypos"		"r90"
		"xpos"		"128" [$X360]
		"wide"		"125" [$WIN32]
		"wide"		"95" [$X360]
		"tall"		"20"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1" [$WIN32]
		"visible"		"0" [$X360]
		"enabled"		"1"
		"labelText"		"#TF_Spectator_CycleTargetRev"
		"textAlignment"		"west"
		"font"		"HM_SpecHint"
	}
	"TipLabel"
	{
		"ControlName"		"CExLabel"
		"fieldName"		"TipLabel"
		"xpos"		"15"
		"xpos_hidef"		"60"
		"xpos_lodef"		"45"
		"ypos"		"r67"
		"ypos_lodef"		"28"
		"ypos_hidef"		"35"
		"wide"		"145"
		"wide_hidef"		"230"
		"wide_lodef"		"240"
		"tall"		"64"
		"tall_hidef"		"70"
		"tall_lodef"		"70"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"labelText"		"%tip%"
		"textAlignment"		"center" [$WIN32]
		"textAlignment"		"north-west" [$X360]
		"font"		"HM_SpecHint"
		"wrap"		"1"
	}
	"itempanel"
	{
		"ControlName"		"CItemModelPanel"
		"fieldName"		"itempanel"
		"xpos"		"0"
		"ypos"		"0"
		"zpos"		"10"
		"wide"		"190"
		"tall"		"100"
		"visible"		"0"
		"bgcolor_override"		"255 255 255 0"
		"PaintBackgroundType"		"0"
		"model_ypos"		"10"
		"model_center_x"		"1"
		"model_wide"		"90"
		"model_tall"		"60"
		"text_xpos"		"10"
		"text_ypos"		"10"
		"text_wide"		"170"
		"text_center"		"1"
		"max_text_height"		"100"
		"padding_height"		"10"
		"resize_to_text"		"1"
		"text_forcesize"		"2"
		"itemmodelpanel"
		{
			"fieldName"		"itemmodelpanel"
			"use_item_rendertarget"		"0"
			"useparentbg"		"1"
		}
		"ItemLabel"
		{
			"ControlName"		"Label"
			"fieldName"		"ItemLabel"
			"font"		"DefaultSmall"
			"xpos"		"10"
			"ypos"		"3"
			"zpos"		"1"
			"wide"		"270"
			"tall"		"9"
			"autoResize"		"0"
			"pinCorner"		"0"
			"visible"		"1"
			"enabled"		"1"
			"labelText"		"#FreezePanel_Item"
			"textAlignment"		"Left"
			"dulltext"		"0"
			"brighttext"		"0"
		}
	}
	"spectator_extras"
	{
		"ControlName"		"EditablePanel"
		"fieldName"		"spectator_extras"
		"xpos"		"0"
		"ypos"		"0"
		"wide"		"f0"
		"tall"		"480"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
	}
}
