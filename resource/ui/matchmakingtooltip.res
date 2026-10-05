// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).
"Resource/UI/MatchMakingTooltip.res"
{
	"TooltipPanel"
	{
		"fieldName"		"TooltipPanel"
		"xpos"		"0"
		"ypos"		"0"
		"zpos"		"30000"
		"wide"		"300"
		"tall"		"100"
		"visible"		"0"
		"PaintBackgroundType"		"2"
		"border"		"MainMenuBGBorder"
		"mouseinputenabled"		"0"
		"TipLabel"
		{
			"ControlName"		"CExLabel"
			"fieldName"		"TipLabel"
			"if_small"
			{
				"font"		"FontStoreOriginalPrice"
			}
			"if_medium"
			{
				"font"		"HudFontSmall"
			}
			"if_large"
			{
				"font"		"HudFontSmallBold"
			}
			"labelText"		"%tiptext%"
			"textAlignment"		"center"
			"xpos"		"10"
			"ypos"		"10"
			"zpos"		"2"
			"wide"		"140"
			"tall"		"30"
			"autoResize"		"0"
			"pinCorner"		"0"
			"visible"		"1"
			"enabled"		"1"
			"fgcolor_override"		"208 209 209 255"
			"auto_wide_tocontents"		"1"
			"auto_tall_tocontents"		"1"
			"centerwrap"		"1"
		}
	}
}
