"""
    Why does this project exist?
    ============================
    Yes, Tkinter is old, and so often under-appreciated or overlooked for building modern GUI's. And yet, its theme
    engine is extremely powerful. This project was created to harness the power of ttk's (and thus Python's) existing
    built-in theme engine to create modern and professional-looking user interfaces which are inspired by, and in many
    cases, whole-sale rip-off's of the themes found on https://bootswatch.com/. Even better, you have the abilty to
    create and use your own custom themes using :ref:`TTK Creator <ttkcreator>`.

    A bootstrap approach to style
    =============================
    Many people are familiar with bootstrap for web developement. It comes pre-packaged with built-in css style classes
    that provide a professional and consistent api for quick development. I took a similar approach with this project
    by pre-defining styles for nearly all ttk widgets. This makes is very easy to apply the theme colors to various
    widgets by using style declarations. If you want a button in the `secondary` theme color, simply apply the
    ``secondary.TButton`` style to the button. Want a blue outlined button? Apply the ``info.Outline.TButton`` style to
    the button.

    What about the old tkinter widgets?
    ===================================
    Some of the ttk widgets utilize existing tkinter widgets. For example: there is a tkinter popdown list in the
    ``ttk.Combobox`` and a legacy tkinter widget inside the ``ttk.OptionMenu``. To make sure these widgets didn't stick
    out like a sore thumb, I created a ``StyleTK`` class to apply the same color and style to these legacy widgets.
    While these legacy widgets are not necessarily intended to be used (and will probably not look as nice as the ttk
    versions when they exist), they are available if needed, and shouldn't look completely out-of-place in your
    ttkbootstrap themed application.
"""
import json
import colorsys
from pathlib import Path
import importlib.resources
from tkinter import ttk
from PIL import ImageTk, Image, ImageDraw


class Style(ttk.Style):
    """
    A class for setting the application style.
    """

    def __init__(self, theme='flatly', *args, **kwargs):
        """
        :param str theme: the name of the theme to use at runtime; *flatly* by default.
        """
        super().__init__(*args, **kwargs)
        self.themes = {}
        self._load_themes()
        self.theme_use(themename=theme)

    @property
    def colors(self):
        theme = self.theme_use()
        if theme in self.themes:
            return self.themes.get(theme).theme.colors
        else:
            return Colors()

    def _load_themes(self):
        """
        Load all ttkbootstrap defined themes
        """
        # pre-defined themes
        json_data = importlib.resources.read_text('ttkbootstrap', 'themes.json')
        builtin_themes = json.loads(json_data)

        # user defined themes
        user_path = Path(builtin_themes['userpath'])
        if user_path.exists():
            with user_path.open(encoding='utf-8') as f:
                user_themes = json.load(f)
        else:
            user_themes = {'themes': []}

        # combined theme collection
        settings = {'themes': builtin_themes['themes'] + user_themes['themes']}

        for theme in settings['themes']:
            if theme['name'] not in self.theme_names():
                settings = ThemeDefinition(
                    name=theme['name'],
                    themetype=theme['type'],
                    font=theme['font'],
                    colors=Colors(**theme['colors']))
                self.themes[settings.name] = StylerTTK(self, settings)

    def theme_use(self, themename=None):
        """
        If themename is None, returns the theme in use, otherwise, set the current theme to themename, refreshes all
        widgets and emits a ``<<ThemeChanged>>`` event.

        Only use this method if you are changing the theme *during* runtime. Otherwise, pass the theme name into the
        Style constructor to instantiate the style with a theme.

        :param str themename: the theme to apply when creating new widgets
        """
        if not themename:
            return super().theme_use()

        if all([themename, themename not in self.theme_names()]):
            print(f"{themename} is not a valid theme name. Please try one of the following:")
            print(self.theme_names())
            return

        if themename in self.themes:
            try:
                super().theme_use(themename)
                current = self.themes.get(themename)
                if current:
                    current.styler_tk.style_tkinter_widgets()
                return
            except AttributeError:
                return
        else:
            super().theme_use(themename)


class ThemeDefinition:
    """
    A class to provide defined name, colors, and font settings for a ttkbootstrap theme.

    :param str name: The name of the theme
    :param str themetype: type: 'light' or 'dark'
    :param str font: Default font to apply to theme. Helvetica is used by default.
    :param Color colors: An instance of the `Colors` class.
    """

    def __init__(self, name='default', themetype='light', font='helvetica', colors=None):
        self.name = name
        self.type = themetype
        self.font = font
        self.colors = colors if colors else Colors()

    def __repr__(self):
        return f'name={self.name}, type={self.type}, font={self.font}, colors={self.colors}'


class Colors:
    """
    A collection of colors used in a ttkbootstrap theme definition.

    :param str primary: the primary theme color; is used as basis for all widgets
    :param str secondary: an accent color; typically the same as `selectbg` in built-in themes
    :param str success: an accent color; an orange hue in most themes
    :param str info: an accent color; a blue hue in most themes
    :param str warning: an accent color; an orange hue in most themes
    :param str danger: an accent color; a red hue in most themes
    :param str bg: background color; used for root window background
    :param str fg: primary font color; used for labels and non-input related widgets
    :param str selectfg: foreground color of selected text
    :param str selectbg: background color of selected text background
    :param str light: a color used for input widget background and trough color
    :param str border: a color used on the border of several input widgets (combobox, entry, spinbox, etc...)
    :param str inputfg: a color used for input widgets; typically a reverse lightness of `fg`
    """

    def __init__(self, **kwargs):
        self.primary = kwargs.get('primary', '#ffffff')
        self.secondary = kwargs.get('secondary', '#ffffff')
        self.success = kwargs.get('success', '#ffffff')
        self.info = kwargs.get('info', '#ffffff')
        self.warning = kwargs.get('warning', '#ffffff')
        self.danger = kwargs.get('danger', '#ffffff')
        self.bg = kwargs.get('bg', '#ffffff')
        self.fg = kwargs.get('fg', '#000000')
        self.selectbg = kwargs.get('selectbg', '#000000')
        self.selectfg = kwargs.get('selectfg', '#ffffff')
        self.light = kwargs.get('light', '#ffffff')
        self.border = kwargs.get('border', '#000000')
        self.inputfg = kwargs.get('inputfg', '#000000')

    def get(self, color_label):
        """
        Lookup a color property

        :param str color_label: a color label corresponding to a class propery (primary, secondary, success, etc...)

        :returns: a hexadecimal color value
        :rtype: str
        """
        return self.__dict__.get(color_label)

    def set(self, color_label, color_value):
        """
        Set a color property

        :param str color_label: the name of the color to be set (key)
        :param str color_value: a hexadecimal color value

        Example::

            set('primary', '#fafafa')
        """
        self.__dict__[color_label] = color_value

    def __iter__(self):
        return iter(['primary', 'secondary', 'success', 'info', 'warning', 'danger'])

    def __repr__(self):
        return str((tuple(zip(self.__dict__.keys(), self.__dict__.values()))))

    @staticmethod
    def label_iter():
        """
         Iterates over all color label properties in the Color class

         :returns: an iterator representing the name of the color properties
         :rtype: iter[str]
        """
        return iter(['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'bg', 'fg', 'selectbg', 'selectfg',
                     'light', 'border', 'inputfg'])

    @staticmethod
    def hex_to_rgb(color):
        """
        Convert hexadecimal color to rgb color value

        :param str color: hexadecimal color value

        :returns: rgb color value
        :rtype: tuple
        """
        if len(color) == 4:
            # 3 digit hexadecimal colors
            r = round(int(color[1], 16) / 255, 2)
            g = round(int(color[2], 16) / 255, 2)
            b = round(int(color[3], 16) / 255, 2)
        else:
            # 6 digit hexadecimal colors
            r = round(int(color[1:3], 16) / 255, 2)
            g = round(int(color[3:5], 16) / 255, 2)
            b = round(int(color[5:], 16) / 255, 2)
        return r, g, b

    @staticmethod
    def rgb_to_hex(r, g, b):
        """
        Convert rgb to hexadecimal color value

        :param int r: red
        :param int g: green
        :param int b: blue

        :returns: a hexadecimal color value
        :rtype: str
        """
        r_ = int(r * 255)
        g_ = int(g * 255)
        b_ = int(b * 255)
        return '#{:02x}{:02x}{:02x}'.format(r_, g_, b_)

    @staticmethod
    def brightness(hex_color, pct_change):
        """
        Adjust the value of a given hexadecimal color. The percent change is expected to be a float.

        To return a *lighter* color, use a positive floating value::

            Colors.brightness('#fafafa', 0.15)

        To return a *darker* color, use a negative floating value::

            Colors.brightness('#fafafa', -0.15)

        :param str hex_color: hexadecimal color
        :param float pct_change: a floating value

        :returns: a lightened or darkened hexadecimal color value
        :rtype: str
        """
        r, g, b = Colors.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        v_ = (1 + pct_change) * v
        v_max = max(0, v_)
        v_min = min(1, v_max)
        r_, g_, b_ = colorsys.hsv_to_rgb(h, s, v_min)
        return Colors.rgb_to_hex(r_, g_, b_)


class StylerTK:
    """
    A class for styling tkinter widgets (not ttk).

    :param parent: an instance of `StylerTTK`
    """

    def __init__(self, parent):
        self.master = parent.style.master
        self.theme = parent.theme

    def style_tkinter_widgets(self):
        """
        A wrapper on all widget style methods. Applies current theme to all standard tkinter widgets
        """
        self._style_window()
        self._style_button()
        self._style_label()
        self._style_checkbutton()
        self._style_radiobutton()
        self._style_entry()
        self._style_scale()
        self._style_listbox()
        self._style_spinbox()
        self._style_menu()
        self._style_menubutton()
        self._style_labelframe()
        self._style_scrollbar()
        self._style_optionmenu()
        self._style_textwidget()
        self._style_combobox()

    def _set_option(self, *args):
        """
        A convenience method to shorten the call to ``option_add``. *Laziness is next to godliness*.
        """
        self.master.option_add(*args)

    def _style_window(self):
        """
        Apply global options to all matching ``tkinter`` widgets
        """
        self.master.configure(background=self.theme.colors.bg)
        self._set_option('*background', self.theme.colors.bg, 20)
        self._set_option('*font', self.theme.font)
        self._set_option('*borderWidth', 0, 20)
        self._set_option('*relief', 'flat', 20)
        self._set_option('*activeBackground', self.theme.colors.selectbg, 20)
        self._set_option('*activeForeground', self.theme.colors.selectfg, 20)
        self._set_option('*selectBackground', self.theme.colors.selectbg, 20)
        self._set_option('*selectForeground', self.theme.colors.selectfg, 20)
        self._set_option('*Text*background', self.theme.colors.light)
        self._set_option('*Text*foreground', self.theme.colors.inputfg)

    def _style_combobox(self):
        """
        Apply style for listbox on ``ttk.Combobox``
            option add *TCombobox*Listbox.background color
            option add *TCombobox*Listbox.font font
            option add *TCombobox*Listbox.foreground color
            option add *TCombobox*Listbox.selectBackground color
            option add *TCombobox*Listbox.selectForeground color
        """
        self._set_option('*TCombobox*Listbox.background', self.theme.colors.bg)

    def _style_button(self):
        """
        Apply style to ``tkinter.Button``
        """
        self._set_option('*Button.foreground', self.theme.colors.selectfg)
        self._set_option('*Button.background', self.theme.colors.primary)

    def _style_label(self):
        """
        Apply style to ``tkinter.Label``
        """
        self._set_option('*Label.foreground', self.theme.colors.fg)
        self._set_option('*Label.background', self.theme.colors.bg)

    def _style_checkbutton(self):
        """
        Apply style to ``tkinter.Checkbutton``
        """
        self._set_option('*Checkbutton.background', self.theme.colors.bg)
        self._set_option('*Checkbutton.foreground', self.theme.colors.fg)
        self._set_option('*Checkbutton.selectColor',
                         self.theme.colors.primary if self.theme.type == 'dark' else 'white')

    def _style_radiobutton(self):
        """
        Apply style to ``tkinter.Radiobutton``
        """
        self._set_option('*Radiobutton.background', self.theme.colors.bg)
        self._set_option('*Radiobutton.foreground', self.theme.colors.fg)
        self._set_option('*Radiobutton.selectColor',
                         self.theme.colors.primary if self.theme.type == 'dark' else 'white')

    def _style_entry(self):
        """
        Apply style to ``tkinter.Entry``
        """
        self._set_option('*Entry.relief', 'flat')
        self._set_option('*Entry.background',
                         (self.theme.colors.light if self.theme.type == 'light' else
                          Colors.brightness(self.theme.colors.light, -0.1)))
        self._set_option('*Entry.foreground', self.theme.colors.fg)
        self._set_option('*Entry.highlightThickness', 1)
        self._set_option('*Entry.highlightBackground', self.theme.colors.border)
        self._set_option('*Entry.highlightColor', self.theme.colors.primary)

    def _style_scale(self):
        """
        Apply style to ``tkinter.Scale``
        """
        self._set_option('*Scale.background', self.theme.colors.primary)
        self._set_option('*Scale.showValue', False)
        self._set_option('*Scale.sliderRelief', 'flat')
        self._set_option('*Scale.highlightThickness', 1)
        self._set_option('*Scale.highlightColor', self.theme.colors.primary)
        self._set_option('*Scale.highlightBackground', self.theme.colors.border)
        self._set_option('*Scale.troughColor',
                         (self.theme.colors.light if self.theme.type == 'light' else
                          Colors.brightness(self.theme.colors.light, -0.1)))

    def _style_spinbox(self):
        """
        Apply style to `tkinter.Spinbox``
        """
        self._set_option('*Spinbox.foreground', self.theme.colors.fg)
        self._set_option('*Spinbox.background',
                         (self.theme.colors.light if self.theme.type == 'light' else
                          Colors.brightness(self.theme.colors.light, -0.1)))
        self._set_option('*Spinbox.highlightThickness', 1)
        self._set_option('*Spinbox.highlightColor', self.theme.colors.primary)
        self._set_option('*Spinbox.highlightBackground', self.theme.colors.border)

    def _style_listbox(self):
        """
        Apply style to ``tkinter.Listbox``
        """
        self._set_option('*Listbox.foreground', self.theme.colors.fg)
        self._set_option('*Listbox.background',
                         (self.theme.colors.light if self.theme.type == 'light' else
                          Colors.brightness(self.theme.colors.light, -0.1)))
        self._set_option('*Listbox.relief', 'flat')
        self._set_option('*Listbox.activeStyle', 'none')
        self._set_option('*Listbox.highlightThickness', 1)
        self._set_option('*Listbox.highlightColor', self.theme.colors.primary)
        self._set_option('*Listbox.highlightBackground', self.theme.colors.border)

    def _style_menubutton(self):
        """
        Apply style to ``tkinter.Menubutton``
        """
        self._set_option('*Menubutton.background', self.theme.colors.primary)
        self._set_option('*Menubutton.foreground', self.theme.colors.selectfg)

    def _style_menu(self):
        """
        Apply style to ``tkinter.Menu``
        """
        self._set_option('*Menu.tearOff', 0)
        self._set_option('*Menu.foreground', self.theme.colors.fg)
        self._set_option('*Menu.selectColor', self.theme.colors.primary)

    def _style_labelframe(self):
        """
        Apply style to ``tkinter.Labelframe``
        """
        self._set_option('*Labelframe.foreground', self.theme.colors.fg)
        self._set_option('*Labelframe.highlightColor', self.theme.colors.border)
        self._set_option('*Labelframe.highlightBackground', self.theme.colors.border)
        self._set_option('*Labelframe.highlightThickness', 1)

    def _style_scrollbar(self):
        """
        Apply style to ``tkinter.Scrollbar``

        .. warning::
            It appears this widget can only be styled in the constructor**
        """

        pass

    def _style_optionmenu(self):
        """
        Apply style to ``tkinter.OptionMenu``

        .. warning::
            It appears this widget can only be styled in the constructor
        """
        pass

    def _style_separator(self):
        """
        Apply style to ``tkinter.Separator``

        .. warning::
            Not implemented
        """
        pass

    def _style_textwidget(self):
        """
        Apply style to ``tkinter.Text``
        """
        self._set_option('*Text*background', self.theme.colors.light)
        self._set_option('*Text*foreground', self.theme.colors.inputfg)




class StylerTTK:
    """
    A class to create a new ttk theme.

    :param Style style: An instance of ``ttk.Style`` class
    :param ThemeDefinition definition: creates the settings for the theme to be created
    """

    def __init__(self, style, definition):
        self.style = style
        self.theme = definition
        self.settings = {}
        self.styler_tk = StylerTK(self)
        self.create_theme()

    def create_theme(self):
        """
        Create and style a new ttk theme. A wrapper around internal style methods.
        """
        self.update_ttk_theme_settings()
        self.style.theme_create(self.theme.name, 'clam', self.settings)

    def update_ttk_theme_settings(self):
        """
        Update the settings dictionary that is used to create a theme. This is a wrapper on all the `_style_widget`
        methods which define the layout, configuration, and styling mapping for each ttk widget.
        """
        self._style_defaults()
        self._style_spinbox()
        self._style_scale()
        self._style_scrollbar()
        self._style_combobox()
        self._style_frame()
        self._style_checkbutton()
        self._style_entry()
        self._style_label()
        self._style_labelframe()
        self._style_notebook()
        self._style_outline_buttons()
        self._style_outline_menubutton()
        self._style_progressbar()
        self._style_radiobutton()
        self._style_solid_buttons()
        self._style_solid_menubutton()
        self._style_treeview()
        self._style_separator()
        self._style_panedwindow()
        pass

    def _style_defaults(self):
        """
        Setup the default ``ttk.Style`` configuration. These defaults are applied to any widget that contains these
        element options. This method should be called *first* before any other style is applied during theme creation.
        """
        self.settings.update({
            '.': {
                'configure': {
                    'background': self.theme.colors.bg,
                    'darkcolor': self.theme.colors.border,
                    'foreground': self.theme.colors.fg,
                    'troughcolor': self.theme.colors.bg,
                    'selectbg': self.theme.colors.selectbg,
                    'selectfg': self.theme.colors.selectfg,
                    'selectforeground': self.theme.colors.selectfg,
                    'selectbackground': self.theme.colors.selectbg,
                    'fieldbg': 'white',
                    'font': self.theme.font,
                    'borderwidth': 1,
                    'focuscolor': ''}}})

    def _style_combobox(self):
        """
        Create style configuration for ``ttk.Combobox``. This element style is created with a layout that combines
        *clam* and *default* theme elements.

        The options available in this widget based on this layout include:

            * Combobox.downarrow: arrowsize, background, bordercolor, relief, arrowcolor
            * Combobox.field: bordercolor, lightcolor, darkcolor, fieldbackground
            * Combobox.padding: padding, relief, shiftrelief
            * Combobox.textarea: font, width

        **NOTE:**

            When the dark theme is used, I used the *spinbox.field* from the *default* theme because the background
            shines through the corners using the `clam` theme. This is an unfortuate hack to make it look ok. Hopefully
            there will be a more permanent/better solution in the future.
        """
        self.settings.update({
            'Combobox.downarrow': {'element create': ('from', 'default')},
            'Combobox.padding': {'element create': ('from', 'clam')},
            'Combobox.textarea': {'element create': ('from', 'clam')},
            'TCombobox': {
                'layout': [('combo.Spinbox.field', {'side': 'top', 'sticky': 'we', 'children': [
                    ('Combobox.downarrow', {'side': 'right', 'sticky': 'ns'}),
                    ('Combobox.padding', {'expand': '1', 'sticky': 'nswe', 'children': [
                        ('Combobox.textarea', {'sticky': 'nswe'})]})]})],
                'configure': {
                    'bordercolor': self.theme.colors.border,
                    'darkcolor': self.theme.colors.bg,
                    'lightcolor': self.theme.colors.bg,
                    'arrowcolor': self.theme.colors.inputfg,
                    'foreground': self.theme.colors.inputfg,
                    'fieldbackground ': self.theme.colors.light,
                    'background ': self.theme.colors.light,
                    'relief': 'flat',
                    'borderwidth ': 0,
                    'padding': 5,
                    'arrowsize ': 16},
                'map': {
                    'bordercolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.bg)],
                    'lightcolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.primary)],
                    'darkcolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.primary)],
                    'arrowcolor': [
                        ('pressed', self.theme.colors.light),
                        ('focus', self.theme.colors.inputfg),
                        ('hover', self.theme.colors.primary)]}}})

        if self.theme.type == 'dark':
            self.settings.update({
                'combo.Spinbox.field': {'element create': ('from', 'default')}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TCombobox': {
                    'map': {
                        'bordercolor': [
                            ('focus', self.theme.colors.get(color)),
                            ('hover', self.theme.colors.get(color))],
                        'lightcolor': [
                            ('focus', self.theme.colors.get(color)),
                            ('pressed', self.theme.colors.get(color))],
                        'darkcolor': [
                            ('focus', self.theme.colors.get(color)),
                            ('pressed', self.theme.colors.get(color))],
                        'arrowcolor': [
                            ('pressed', self.theme.colors.light),
                            ('focus', self.theme.colors.inputfg),
                            ('hover', self.theme.colors.primary)]}}})

    def _style_separator(self):
        """
        Create style configuration for ttk separator: *ttk.Separator*. The default style for light will be border, but
        dark will be primary, as this makes the most sense for general use. However, all other colors will be available
        as well through styling.

        The options avaiable in this widget include:

            - Separator.separator: orient, background
        """
        self.settings.update({
            'Horizontal.TSeparator': {
                'configure': {
                    'background': (
                        self.theme.colors.border if self.theme.type == 'light' else self.theme.colors.primary)}},
            'Vertical.TSeparator': {
                'configure': {
                    'background': (
                        self.theme.colors.border if self.theme.type == 'light' else self.theme.colors.primary)}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.Horizontal.TSeparator': {
                    'configure': {
                        'background': self.theme.colors.get(color)}},
                f'{color}.Vertical.TSeparator': {
                    'configure': {
                        'background': self.theme.colors.get(color)}}})

    def _style_progressbar(self):
        """
        Create style configuration for ttk progressbar: *ttk.Progressbar*

        The options available in this widget include:

            - Progressbar.trough: borderwidth, troughcolor, troughrelief
            - Progressbar.pbar: orient, thickness, barsize, pbarrelief, borderwidth, background
        """
        self.settings.update({
            'Progressbar.trough': {'element create': ('from', 'default')},
            'Progressbar.pbar': {'element create': ('from', 'default')},
            'TProgressbar': {'configure': {
                'thickness': 20,
                'borderwidth': 0,
                'troughcolor': Colors.brightness(self.theme.colors.light, -0.05),
                'background': self.theme.colors.primary}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.Horizontal.TProgressbar': {
                    'configure': {
                        'background': self.theme.colors.get(color)}},
                f'{color}.Vertical.TProgressbar': {
                    'configure': {
                        'background': self.theme.colors.get(color)}}})

    @staticmethod
    def _create_slider_image(color, size=18):
        """
        Create a circle slider image based on given size and color; used in the slider widget.

        :param str color: a hexadecimal color value
        :param int size: the size diameter of the slider circle.

        :returns: An image draw in the shape of a circle of the theme color specified
        :rtype: ImageTk.PhotoImage
        """
        im = Image.new('RGBA', (100, 100))
        draw = ImageDraw.Draw(im)
        draw.ellipse((0, 0, 95, 95), fill=color)
        return ImageTk.PhotoImage(im.resize((size, size), Image.LANCZOS))

    def _style_scale(self):
        """
        Create style configuration for ttk scale: *ttk.Scale*

        The options available in this widget include:

            - Scale.trough: borderwidth, troughcolor, troughrelief
            - Scale.slider: sliderlength, sliderthickness, sliderrelief, borderwidth, background, bordercolor, orient
        """
        # create widget images
        self.scale_images = {
            'primary_regular': self._create_slider_image(self.theme.colors.primary),
            'primary_pressed': self._create_slider_image(
                Colors.brightness(self.theme.colors.primary, -0.2)),
            'primary_hover': self._create_slider_image(
                Colors.brightness(self.theme.colors.primary, -0.1)), 'trough': ImageTk.PhotoImage(
                Image.new('RGB', (8, 8), Colors.brightness(self.theme.colors.light, -0.05)))}

        # The layout is derived from the 'xpnative' theme
        self.settings.update({
            'Horizontal.TScale': {
                'layout': [
                    ('Scale.focus', {'expand': '1', 'sticky': 'nswe', 'children': [
                        ('Horizontal.Scale.track', {'sticky': 'we'}),
                        ('Horizontal.Scale.slider', {'side': 'left', 'sticky': ''})]})]},
            'Vertical.TScale': {
                'layout': [
                    ('Scale.focus', {'expand': '1', 'sticky': 'nswe', 'children': [
                        ('Vertical.Scale.track', {'sticky': 'ns'}),
                        ('Vertical.Scale.slider', {'side': 'top', 'sticky': ''})]})]},
            'Scale.track': {'element create': ('image', self.scale_images['trough'])},
            'Scale.slider': {'element create':
                                 ('image', self.scale_images['primary_regular'],
                                  ('pressed', self.scale_images['primary_pressed']),
                                  ('hover', self.scale_images['primary_hover']))}})

        for color in self.theme.colors:
            self.scale_images.update({
                f'{color}_regular': self._create_slider_image(self.theme.colors.get(color)),
                f'{color}_pressed': self._create_slider_image(Colors.brightness(self.theme.colors.get(color), -0.2)),
                f'{color}_hover': self._create_slider_image(
                    Colors.brightness(self.theme.colors.get(color), -0.1)), f'{color}_trough': ImageTk.PhotoImage(
                    Image.new('RGB', (8, 8), Colors.brightness(self.theme.colors.light, -0.05)))})

            # The layout is derived from the 'xpnative' theme
            self.settings.update({
                f'{color}.Horizontal.TScale': {
                    'layout': [
                        ('Scale.focus', {'expand': '1', 'sticky': 'nswe', 'children': [
                            ('Horizontal.Scale.track', {'sticky': 'we'}),
                            (f'{color}.Horizontal.Scale.slider', {'side': 'left', 'sticky': ''})]})]},
                f'{color}.Vertical.TScale': {
                    'layout': [
                        (f'{color}.Scale.focus', {'expand': '1', 'sticky': 'nswe', 'children': [
                            ('Vertical.Scale.track', {'sticky': 'ns'}),
                            (f'{color}.Vertical.Scale.slider', {'side': 'top', 'sticky': ''})]})]},
                f'{color}.Vertical.Scale.slider': {'element create':
                                     ('image', self.scale_images[f'{color}_regular'],
                                      ('pressed', self.scale_images[f'{color}_pressed']),
                                      ('hover', self.scale_images[f'{color}_hover']))},
                f'{color}.Horizontal.Scale.slider': {'element create':
                                                       ('image', self.scale_images[f'{color}_regular'],
                                                        ('pressed', self.scale_images[f'{color}_pressed']),
                                                        ('hover', self.scale_images[f'{color}_hover']))}})

    def _style_scrollbar(self):
        """
        Create style configuration for ttk scrollbar: *ttk.Scrollbar*. This theme uses elements from the *alt* theme to
        build the widget layout.

        The options available in this widget include:

            - Scrollbar.trough: orient, troughborderwidth, troughcolor, troughrelief, groovewidth
            - Scrollbar.uparrow: arrowsize, background, bordercolor, relief, arrowcolor
            - Scrollbar.downarrow: arrowsize, background, bordercolor, relief, arrowcolor
            - Scrollbar.thumb: width, background, bordercolor, relief, orient
        """
        self.settings.update({
            'Vertical.Scrollbar.trough': {'element create': ('from', 'alt')},
            'Vertical.Scrollbar.thumb': {'element create': ('from', 'alt')},
            'Vertical.Scrollbar.uparrow': {'element create': ('from', 'alt')},
            'Vertical.Scrollbar.downarrow': {'element create': ('from', 'alt')},
            'Horizontal.Scrollbar.trough': {'element create': ('from', 'alt')},
            'Horizontal.Scrollbar.thumb': {'element create': ('from', 'alt')},
            'Horizontal.Scrollbar.uparrow': {'element create': ('from', 'alt')},
            'Horizontal.Scrollbar.downarrow': {'element create': ('from', 'alt')},
            'TScrollbar': {'configure': {
                'troughrelief': 'flat',
                'relief': 'flat',
                'troughborderwidth': 2,
                'troughcolor': self.theme.colors.light,
                'background': Colors.brightness(self.theme.colors.light, -0.1),
                'arrowsize': 16,
                'arrowcolor': self.theme.colors.inputfg}}})

    def _style_spinbox(self):
        """
        Create style configuration for ttk spinbox: *ttk.Spinbox*

        This widget uses elements from the *default* and *clam* theme to create the widget layout.
        For dark themes,the spinbox.field is created from the *default* theme element because the background
        color shines through the corners of the widget when the primary theme background color is dark.

        The options available in this widget include:

            - Spinbox.field: bordercolor, lightcolor, darkcolor, fieldbackground
            - spinbox.uparrow: background, relief, borderwidth, arrowcolor, arrowsize
            - spinbox.downarrow: background, relief, borderwidth, arrowcolor, arrowsize
            - spinbox.padding: padding, relief, shiftrelief
            - spinbox.textarea: font, width
        """
        if self.theme.type == 'dark':
            self.settings.update({'Spinbox.field': {'element create': ('from', 'default')}})

        self.settings.update({
            'Spinbox.uparrow': {'element create': ('from', 'default')},
            'Spinbox.downarrow': {'element create': ('from', 'default')},
            'TSpinbox': {
                'layout': [
                    ('custom.Spinbox.field', {'side': 'top', 'sticky': 'we', 'children': [
                        ('null', {'side': 'right', 'sticky': '', 'children': [
                            ('Spinbox.uparrow', {'side': 'top', 'sticky': 'e'}),
                            ('Spinbox.downarrow', {'side': 'bottom', 'sticky': 'e'})]}),
                        ('Spinbox.padding', {'sticky': 'nswe', 'children': [
                            ('Spinbox.textarea', {'sticky': 'nswe'})]})]})],
                'configure': {
                    'fieldbackground': self.theme.colors.light,
                    'bordercolor': self.theme.colors.bg,
                    'lightcolor': self.theme.colors.border,
                    'darkcolor': self.theme.colors.border,
                    'foreground': self.theme.colors.inputfg,
                    'borderwidth': 0,
                    'background': self.theme.colors.light,
                    'relief': 'flat',
                    'arrowcolor': self.theme.colors.inputfg,
                    'arrowsize': 16,
                    'padding': (10, 5)
                },
                'map': {
                    'bordercolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.bg)],
                    'lightcolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.primary)],
                    'darkcolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.primary)],
                    'arrowcolor': [
                        ('pressed', self.theme.colors.primary),
                        ('focus', self.theme.colors.inputfg),
                        ('hover', self.theme.colors.inputfg)]}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TSpinbox': {
                    'map': {
                        'bordercolor': [
                            ('focus', self.theme.colors.get(color)),
                            ('hover', self.theme.colors.get(color))],
                        'arrowcolor': [
                            ('pressed', self.theme.colors.get(color)),
                            ('pressed', self.theme.colors.inputfg),
                            ('hover', self.theme.colors.inputfg)],
                        'lightcolor': [('focus', self.theme.colors.get(color))],
                        'darkcolor': [('focus', self.theme.colors.get(color))]}}})

    def _style_treeview(self):
        """
        Create style configuration for ttk treeview: *ttk.Treeview*. This widget uses elements from the *alt* and *clam*
         theme to create the widget layout.

        The options available in this widget include:

            Treeview:

                - Treeview.field: bordercolor, lightcolor, darkcolor, fieldbackground
                - Treeview.padding: padding, relief, shiftrelief
                - Treeview.treearea:
                - Treeitem.padding: padding, relief, shiftrelief
                - Treeitem.indicator: foreground, diameter, indicatormargins
                - Treeitem.image: image, stipple, background
                - Treeitem.focus: focuscolor, focusthickness
                - Treeitem.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed

            Treeheading:

                - Treeheading.cell: background, rownumber
                - Treeheading.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
                - Treeheading.padding: padding, relief, shiftrelief
                - Treeheading.image: image, stipple, background
                - Treeheading.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed
        """
        self.settings.update({
            'Treeview': {
                'layout': [
                    ('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [
                        ('Treeview.padding', {'sticky': 'nswe', 'children': [
                            ('Treeview.treearea', {'sticky': 'nswe'})]})]})],
                'configure': {
                    'background': self.theme.colors.light,
                    'foreground': self.theme.colors.inputfg,
                    'bordercolor': self.theme.colors.border,
                    'lightcolor': self.theme.colors.bg,
                    'darkcolor': self.theme.colors.bg,
                    'relief': 'raised' if self.theme.type == 'light' else 'flat',
                    'padding': -1 if self.theme.type == 'light' else -2},
                'map': {
                    'background': [('selected', self.theme.colors.selectbg)],
                    'foreground': [('selected', self.theme.colors.selectfg)],
                    'bordercolor': [('focus', self.theme.colors.border)]}},
            'Treeview.Heading': {
                'configure': {
                    'background': self.theme.colors.primary,
                    'foreground': self.theme.colors.selectfg,
                    'relief': 'flat',
                    'padding': 5}},
            'Treeitem.indicator': {'element create': ('from', 'alt')}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.Treeview.Heading': {
                    'configure': {
                        'background': self.theme.colors.get(color)},
                    'map': {
                        'bordercolor': [('focus', self.theme.colors.get(color))]}}})

    def _style_frame(self):
        """
        Create style configuration for ttk frame: *ttk.Frame*

        The options available in this widget include:

            - Frame.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
        """
        self.settings.update({
            'TFrame': {'configure': {'background': self.theme.colors.bg}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TFrame': {'configure': {'background': self.theme.colors.get(color)}}})

    def _style_solid_buttons(self):
        """
        Apply a solid color style to ttk button: *ttk.Button*

        The options available in this widget include:

            - Button.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Button.focus: focuscolor, focusthickness
            - Button.padding: padding, relief, shiftrelief
            - Button.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        self.settings.update({
            'TButton': {
                'configure': {
                    'foreground': self.theme.colors.selectfg,
                    'background': self.theme.colors.primary,
                    'bordercolor': self.theme.colors.primary,
                    'darkcolor': self.theme.colors.primary,
                    'lightcolor': self.theme.colors.primary,
                    'anchor': 'center',
                    'relief': 'raised',
                    'focusthickness': 0,
                    'focuscolor': '',
                    'padding': (10, 5)},
                'map': {
                    'background': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'bordercolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'darkcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'lightcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))]}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TButton': {
                    'configure': {
                        'foreground': self.theme.colors.selectfg,
                        'background': self.theme.colors.get(color),
                        'bordercolor': self.theme.colors.get(color),
                        'darkcolor': self.theme.colors.get(color),
                        'lightcolor': self.theme.colors.get(color),
                        'relief': 'raised',
                        'focusthickness': 0,
                        'focuscolor': '',
                        'padding': (10, 5)},
                    'map': {
                        'background': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'bordercolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'darkcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'lightcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))]}}})

    def _style_outline_buttons(self):
        """
        Apply an outline style to ttk button: *ttk.Button*. This button has a solid button look on focus and
        hover.

        The options available in this widget include:

            - Button.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Button.focus: focuscolor, focusthickness
            - Button.padding: padding, relief, shiftrelief
            - Button.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        self.settings.update({
            'Outline.TButton': {
                'configure': {
                    'foreground': self.theme.colors.primary,
                    'background': self.theme.colors.bg,
                    'bordercolor': self.theme.colors.primary,
                    'darkcolor': self.theme.colors.bg,
                    'lightcolor': self.theme.colors.bg,
                    'relief': 'raised',
                    'focusthickness': 0,
                    'focuscolor': '',
                    'padding': (10, 5)},
                'map': {
                    'foreground': [
                        ('pressed', self.theme.colors.selectfg),
                        ('hover', self.theme.colors.selectfg)],
                    'background': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'bordercolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'darkcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'lightcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))]}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.Outline.TButton': {
                    'configure': {
                        'foreground': self.theme.colors.get(color),
                        'background': self.theme.colors.bg,
                        'bordercolor': self.theme.colors.get(color),
                        'darkcolor': self.theme.colors.bg,
                        'lightcolor': self.theme.colors.bg,
                        'relief': 'raised',
                        'focusthickness': 0,
                        'focuscolor': '',
                        'padding': (10, 5)},
                    'map': {
                        'foreground': [
                            ('pressed', self.theme.colors.selectfg),
                            ('hover', self.theme.colors.selectfg)],
                        'background': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'bordercolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'darkcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'lightcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))]}}})

    def _style_entry(self):
        """
        Create style configuration for ttk entry: *ttk.Entry*

        The options available in this widget include:

            - Entry.field: bordercolor, lightcolor, darkcolor, fieldbackground
            - Entry.padding: padding, relief, shiftrelief
            - Entry.textarea: font, width
        """
        self.settings.update({
            'TEntry': {
                'configure': {
                    'fieldbackground': self.theme.colors.light,
                    'bordercolor': self.theme.colors.bg,
                    'lightcolor': self.theme.colors.border,
                    'darkcolor': self.theme.colors.border,
                    'foreground': self.theme.colors.inputfg,
                    'padding': 5},
                'map': {
                    'bordercolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.bg)],
                    'lightcolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.primary)],
                    'darkcolor': [
                        ('focus', self.theme.colors.primary),
                        ('hover', self.theme.colors.primary)]}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TEntry': {
                'map': {
                    'bordercolor': [('focus', self.theme.colors.get(color))],
                    'lightcolor': [('focus', self.theme.colors.get(color))],
                    'darkcolor': [('focus', self.theme.colors.get(color))]}}})

    def _style_radiobutton(self):
        """
        Create style configuration for ttk radiobutton: *ttk.Radiobutton*

        The options available in this widget include:

            - Radiobutton.padding: padding, relief, shiftrelief
            - Radiobutton.indicator: indicatorsize, indicatormargin, indicatorbackground, indicatorforeground,
                upperbordercolor, lowerbordercolor
            - Radiobutton.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background

        **NOTE:**

            On Windows, the button defaults to the 'xpnative' theme look. This means that you cannot change the look
            and feel with styles. On Linux and MacOS, defaults to stylized 'clam' theme, so the style can be changed.
        """
        if 'xpnative' in self.style.theme_names():
            self.settings.update({
                'Radiobutton.indicator': {
                    'element create': ('from', 'xpnative')}})

        self.settings.update({
            'TRadiobutton': {
                'configure': {
                    'indicatormargin': 8,
                    'indicatorsize': 12,
                    'upperbordercolor': (
                        self.theme.colors.fg if self.theme.type == 'light' else self.theme.colors.light),
                    'lowerbordercolor': (
                        self.theme.colors.fg if self.theme.type == 'light' else self.theme.colors.light),
                    'indicatorforeground': (
                        self.theme.colors.fg if self.theme.type == 'light' else self.theme.colors.bg)},
                'map': {
                    'foreground': [('active', self.theme.colors.primary)],
                    'indicatorforeground': [
                        ('active', self.theme.colors.primary if (self.theme.type == 'light') else 'black')]}}})

        # variations change the indicator color
        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TRadiobutton': {
                    'map': {
                        'foreground': [('active', Colors.brightness(self.theme.colors.get(color), -0.2))],
                        'indicatorforeground': [
                            ('active', Colors.brightness(self.theme.colors.get(color), -0.2))]}}})

    def _style_label(self):
        """
        Create style configuration for ttk label: *ttk.Label*

        The options available in this widget include:

            - Label.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Label.padding: padding, relief, shiftrelief
            - Label.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        self.settings.update({
            'TLabel': {'configure': {'foreground': self.theme.colors.fg}}})

        # self.style.configure('TLabel', foreground=self.settings.colors.fg)
        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TLabel': {
                    'configure': {
                        'foreground': self.theme.colors.get(color)}}})

    def _style_labelframe(self):
        """
        Create style configuration for ttk labelframe: *ttk.LabelFrame*

        The options available in this widget include:

            - Labelframe.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Label.fill: background
            - Label.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed
        """
        self.settings.update({
            'TLabelframe': {
                'configure': {
                    'padding': (10, 5),
                    'foreground': self.theme.colors.fg,
                    'relief': 'raised',
                    'bordercolor': self.theme.colors.border,
                    'darkcolor': self.theme.colors.bg,
                    'lightcolor': self.theme.colors.bg}},
            'TLabelframe.Label': {
                'configure': {
                    'foreground': self.theme.colors.fg}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TLabelframe': {
                    'configure': {
                        'foreground': self.theme.colors.get(color),
                        'background': self.theme.colors.get(color)}},
                f'{color}.TLabelframe.Label': {
                    'configure': {
                        'foreground': self.theme.colors.get(color)}}})

    def _style_checkbutton(self):
        """
        Create style configuration for ttk checkbutton: *ttk.Checkbutton*

        The options available in this widget include:

            - Checkbutton.padding: padding, relief, shiftrelief
            - Checkbutton.indicator: indicatorsize, indicatormargin, indicatorbackground, indicatorforeground,
                upperbordercolor, lowerbordercolor
            - Checkbutton.focus: focuscolor, focusthickness
            - Checkbutton.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background

        **NOTE:**
            On Windows, the button defaults to the 'xpnative' theme look. This means that you cannot change the look
            and feel with styles. On Linux and MacOS, defaults to stylized 'clam' theme, so the style can be changed.
        """
        if 'xpnative' in self.style.theme_names():
            self.settings.update({
                'Checkbutton.indicator': {
                    'element create': ('from', 'xpnative')}})

        self.settings.update({
            'TCheckbutton': {
                'configure': {
                    'foreground': self.theme.colors.fg,
                    'indicatorsize': 10,
                    'indicatormargin': 10,
                    'indicatorforeground': self.theme.colors.selectfg},
                'map': {
                    'indicatorbackground': [
                        ('active selected', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('selected', self.theme.colors.fg),
                        ('active !selected', self.theme.colors.light)],
                    'foreground': [
                        ('active', self.theme.colors.primary)]}}})

        # variations change indicator color
        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TCheckbutton': {
                    'map': {
                        'indicatorbackground': [
                            ('active selected', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('selected', self.theme.colors.fg),
                            ('active !selected', self.theme.colors.light)],
                        'indicatorforeground': [
                            ('active selected', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('selected', self.theme.colors.get(color))],
                        'foreground': [
                            ('active', Colors.brightness(self.theme.colors.get(color), -0.2))]}}})

    def _style_solid_menubutton(self):
        """
        Apply a solid color style to ttk menubutton: *ttk.Menubutton*

        The options available in this widget include:

            - Menubutton.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Menubutton.focus: focuscolor, focusthickness
            - Menubutton.indicator: arrowsize, arrowcolor, arrowpadding
            - Menubutton.padding: compound, space, text, font, foreground, underline, width, anchor, justify,
                wraplength, embossed, image, stipple, background
            - Menubutton.label:
        """
        self.settings.update({
            'TMenubutton': {
                'configure': {
                    'foreground': self.theme.colors.selectfg,
                    'background': self.theme.colors.primary,
                    'bordercolor': self.theme.colors.primary,
                    'darkcolor': self.theme.colors.primary,
                    'lightcolor': self.theme.colors.primary,
                    'arrowcolor': self.theme.colors.bg if self.theme.type == 'light' else 'white',
                    'arrowpadding': (0, 0, 15, 0),
                    'relief': 'raised',
                    'focusthickness': 0,
                    'focuscolor': '',
                    'padding': (10, 5)},
                'map': {
                    'background': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'bordercolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'darkcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'lightcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))]}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.TMenubutton': {
                    'configure': {
                        'foreground': self.theme.colors.selectfg,
                        'background': self.theme.colors.get(color),
                        'bordercolor': self.theme.colors.get(color),
                        'darkcolor': self.theme.colors.get(color),
                        'lightcolor': self.theme.colors.get(color),
                        'arrowcolor': self.theme.colors.bg if self.theme.type == 'light' else 'white',
                        'arrowpadding': (0, 0, 15, 0),
                        'relief': 'raised',
                        'focusthickness': 0,
                        'focuscolor': '',
                        'padding': (10, 5)},
                    'map': {
                        'background': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'bordercolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'darkcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'lightcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))]}}})

    def _style_outline_menubutton(self):
        """
        Apply and outline style to ttk menubutton: *ttk.Menubutton*

        The options available in this widget include:

            - Menubutton.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Menubutton.focus: focuscolor, focusthickness
            - Menubutton.indicator: arrowsize, arrowcolor, arrowpadding
            - Menubutton.padding: compound, space, text, font, foreground, underline, width, anchor, justify,
                wraplength, embossed, image, stipple, background
            - Menubutton.label:
        """
        self.settings.update({
            'Outline.TMenubutton': {
                'configure': {
                    'font': self.theme.font,
                    'foreground': self.theme.colors.primary,
                    'background': self.theme.colors.bg,
                    'bordercolor': self.theme.colors.primary,
                    'darkcolor': self.theme.colors.bg,
                    'lightcolor': self.theme.colors.bg,
                    'arrowcolor': self.theme.colors.primary,
                    'arrowpadding': (0, 0, 15, 0),
                    'relief': 'raised',
                    'focusthickness': 0,
                    'focuscolor': '',
                    'padding': (10, 5)},
                'map': {
                    'foreground': [
                        ('pressed', self.theme.colors.selectfg),
                        ('hover', self.theme.colors.selectfg)],
                    'background': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'bordercolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'darkcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'lightcolor': [
                        ('pressed', Colors.brightness(self.theme.colors.primary, -0.2)),
                        ('hover', Colors.brightness(self.theme.colors.primary, -0.1))],
                    'arrowcolor': [
                        ('pressed', self.theme.colors.selectfg),
                        ('hover', self.theme.colors.selectfg)]}}})

        for color in self.theme.colors:
            self.settings.update({
                f'{color}.Outline.TMenubutton': {
                    'configure': {
                        'foreground': self.theme.colors.get(color),
                        'background': self.theme.colors.bg,
                        'bordercolor': self.theme.colors.get(color),
                        'darkcolor': self.theme.colors.bg,
                        'lightcolor': self.theme.colors.bg,
                        'arrowcolor': self.theme.colors.get(color),
                        'arrowpadding': (0, 0, 15, 0),
                        'relief': 'raised',
                        'focusthickness': 0,
                        'focuscolor': '',
                        'padding': (10, 5)},
                    'map': {
                        'foreground': [
                            ('pressed', self.theme.colors.selectfg),
                            ('hover', self.theme.colors.selectfg)],
                        'background': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'bordercolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'darkcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'lightcolor': [
                            ('pressed', Colors.brightness(self.theme.colors.get(color), -0.2)),
                            ('hover', Colors.brightness(self.theme.colors.get(color), -0.1))],
                        'arrowcolor': [
                            ('pressed', self.theme.colors.selectfg),
                            ('hover', self.theme.colors.selectfg)]}}})

    def _style_notebook(self):
        """
        Create style configuration for ttk notebook: *ttk.Notebook*

        The options available in this widget include:

            - Notebook.client: background, bordercolor, lightcolor, darkcolor
            - Notebook.tab: background, bordercolor, lightcolor, darkcolor
            - Notebook.padding: padding, relief, shiftrelief
            - Notebook.focus: focuscolor, focusthickness
            - Notebook.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """

        self.settings.update({
            'TNotebook': {
                'configure': {
                    'bordercolor': self.theme.colors.border,
                    'lightcolor': self.theme.colors.bg if self.theme.type == 'light' else self.theme.colors.selectbg,
                    'borderwidth': 1}},
            'TNotebook.Tab': {
                'configure': {
                    'bordercolor': self.theme.colors.border,
                    'lightcolor': self.theme.colors.bg if self.theme.type == 'light' else self.theme.colors.selectbg,
                    'foreground': self.theme.colors.fg,
                    'padding': (10, 5)},
                'map': {
                    'background': [
                        ('!selected', self.theme.colors.light)],
                    'lightcolor': [
                        ('!selected', self.theme.colors.light)],
                    'darkcolor': [
                        ('!selected', self.theme.colors.light)],
                    'bordercolor': [
                        ('!selected', self.theme.colors.border)],
                    'foreground': [
                        ('!selected', self.theme.colors.inputfg)]}}})

    def _style_panedwindow(self):
        """
        Create style configuration for ttk paned window: *ttk.PanedWindow*

        The options available in this widget include:

            Paned Window:

                - Panedwindow.background: background

            Sash:

                - Sash.hsash: sashthickness
                - Sash.hgrip: lightcolor, bordercolor, gripcount
                - Sash.vsash: sashthickness
                - Sash.vgrip: lightcolor, bordercolor, gripcount
        """
        self.settings.update({
            'TPanedwindow': {
                'configure': {
                    'background': Colors.brightness(self.theme.colors.light, -0.1)}},
            'Sash': {
                'configure': {
                    'bordercolor': self.theme.colors.inputfg,
                    'lightcolor': self.theme.colors.light,
                    'sashthickness': 9,
                    'sashpad': 0,
                    'gripcount': 25}}})

    def _style_sizegroup(self):
        """
        Create style configuration for ttk sizegrip: *ttk.Sizegrip*

        The options available in this widget include:

            - Sizegrip.sizegrip: background

        **NOT IMPLEMENTED as existing styles are already covering this.**
        """
        pass
