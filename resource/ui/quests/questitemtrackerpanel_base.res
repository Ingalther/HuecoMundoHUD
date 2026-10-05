// Hueco Mundo HUD - made by Ingalther Ulquiorra. Licence: CC BY-NC-SA 4.0 (credit required, no selling).
"Resource/UI/QuestItemTrackerPanel_Base.res"
{
	"ItemName"
	{
		"ControlName"		"Label"
		"fieldName"		"ItemName"
		"labeltext"		"%itemname%"
		"xpos"		"rs1"
		"ypos"		"8"
		"wide"		"190"
		"tall"		"18"
		"zpos"		"4"
		"textinsetx"		"5"
		"fgcolor_override"		"208 209 209 255"
		"font"		"AchievementTracker_Name"
		"TextAlignment"		"north-east"
		"proportionaltoparent"		"1"
	}
	"NotYetCommittedContainer"
	{
		"ControlName"		"EditablePanel"
		"fieldName"		"NotYetCommittedContainer"
		"xpos"		"rs1"
		"ypos"		"0"
		"zpos"		"3"
		"wide"		"f0"
		"tall"		"10"
		"visible"		"1"
		"enabled"		"1"
		"proportionaltoparent"		"1"
		"PendingText"
		{
			"ControlName"		"CExLabel"
			"fieldName"		"PendingText"
			"labeltext"		"#QuestTracker_Pending"
			"xpos"		"rs1"
			"ypos"		"0"
			"wide"		"190"
			"tall"		"f0"
			"zpos"		"4"
			"textinsetx"		"5"
			"fgcolor_override"		"208 209 209 255"
			"font"		"QuestObjectiveTracker_Desc"
			"TextAlignment"		"north-east"
			"proportionaltoparent"		"1"
		}
	}
}
