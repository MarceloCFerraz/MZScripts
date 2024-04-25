package colors

import (
	"runtime"
)

var esc = ""
var end = ""

var Black = ""
var Red = ""
var Green = ""
var Yellow = ""
var Blue = ""
var Magenta = ""
var Cyan = ""
var White = ""

var fontFmt = ""
var backgroundFmt = ""
var boldFmt = ""
var italicFmt = ""
var underlineFmt = ""

func Init() {
	// https://en.wikipedia.org/wiki/ANSI_escape_code

	if runtime.GOOS == "windows" {
		return
	}

	esc = "\x1B[" // 0x1B is always esc. octal counterpart is '\033'
	end = esc + "0m"

	fontFmt = esc + "3"
	backgroundFmt = esc + "4"

	Black = "0m"
	Red = "1m"
	Green = "2m"
	Yellow = "3m"
	Blue = "4m"
	Magenta = "5m"
	Cyan = "6m"
	White = "7m"

	boldFmt = esc + "1m"
	italicFmt = esc + "3m"
	underlineFmt = esc + "4m"
}

type Input struct {
	Text      string
	Bold      bool
	Italic    bool
	Underline bool
	FontColor string
	BgColor   string
}

/*
params:

	color: pointer to the desired color
	str:	pointer to original string
	opt:	pointer to either `BgColor` or `fontFmt` properties

return:

	the formatted string in the following format `esc + opt + color + str + end`

example:

	txt := Input{
		Input:      "some text",
		Bold:      true,
		Italic:    true,
		Underline: true,
		FontColor: Red,
		BgColor:   White,
	}
	i.Paint() should return
	`UnderlineInput(
		ItalicInput(
			BoldInput(
				RedFont(
					WhiteBG(
						"some text",
					),
				),
			),
		),
	)`
*/
func (i *Input) Paint() string {
	response := i.Text

	if i.BgColor != "" {
		response = backgroundFmt + i.BgColor + response + end
	}

	if i.FontColor != "" {
		response = fontFmt + i.FontColor + response + end
	}

	if i.Bold {
		response = boldFmt + response + end
	}

	if i.Italic {
		response = italicFmt + response + end
	}

	if i.Underline {
		response = underlineFmt + response + end
	}

	return response
}

func (i *Input) Reset() {
	i.Text = ""
	i.Bold = false
	i.Italic = false
	i.Underline = false
	i.BgColor = ""
	i.FontColor = ""
}
