import functools



class colors:
    # REF https://misc.flogisoft.com/bash/tip_colors_and_formatting
    FG_DEFAULT       = '\033[39m'
    FG_BLACK		 = '\033[30m'
    FG_RED			 = '\033[31m'
    FG_GREEN		 = '\033[32m'
    FG_YELLOW		 = '\033[33m'
    FG_BLUE			 = '\033[34m'
    FG_MAGENTA		 = '\033[35m'
    FG_CYAN			 = '\033[36m'
    FG_LIGHT_GRAY	 = '\033[37m'
    FG_DARK_GRAY	 = '\033[90m'
    FG_LIGHT_RED	 = '\033[91m'
    FG_LIGHT_GREEN	 = '\033[92m'
    FG_LIGHT_YELLOW	 = '\033[93m'
    FG_LIGHT_BLUE	 = '\033[94m'
    FG_LIGHT_MAGENTA = '\033[95m'
    FG_LIGHT_CYAN	 = '\033[96m'
    FG_WHITE		 = '\033[37m'

    # Background Colors
    BG_DEFAULT		 = '\033[49m'
    BG_BLACK		 = '\033[40m'
    BG_RED			 = '\033[41m'
    BG_GREEN		 = '\033[42m'
    BG_YELLOW		 = '\033[43m'
    BG_BLUE			 = '\033[44m'
    BG_MAGENTA		 = '\033[45m'
    BG_CYAN			 = '\033[46m'
    BG_LIGHT_GRAY	 = '\033[47m'
    BG_DARK_GRAY	 = '\033[100m'
    BG_LIGHT_RED	 = '\033[101m'
    BG_LIGHT_GREEN	 = '\033[102m'
    BG_LIGHT_YELLOW	 = '\033[103m'
    BG_LIGHT_BLUE	 = '\033[104m'
    BG_LIGHT_MAGENTA = '\033[105m'
    BG_LIGHT_CYAN	 = '\033[106m'
    BG_WHITE		 = '\033[107m'

    # STYLES
    BOLD             = '\033[1m'
    DIM              = '\033[2m'
    UNDERLINE        = '\033[4m'
    BLINK            = '\033[5m'
    REVERSE          = '\033[7m'
    HIDDEN           = '\033[8m'

    # RESETS
    RESET_ALL        = '\033[0m'
    RESET_BOLD       = '\033[21m'
    RESET_DIM        = '\033[22m'
    RESET_UNDERLINE  = '\033[24m'
    RESET_BLINK      = '\033[25m'
    RESET_REVERSE    = '\033[27m'
    RESET_HIDDEN     = '\033[28m'

    def colorize(s,*props):
        """
        colorize a string with props and reset:
           print(colors.colorize("test",colors.BG_WHITE,colors.FG_BLACK,colors.BOLD))
        """
        p=functools.reduce((lambda p1, p2: p1+p2), props)
        return p+s+colors.RESET_ALL
