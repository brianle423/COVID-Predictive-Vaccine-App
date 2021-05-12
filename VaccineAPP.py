from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.label import Label
from dataanalysis import vaccineDate
from kivy.uix.image import Image, AsyncImage

Builder.load_string('''
<DDButton@Button>:
    size_hint_y: None
    size_hint_x: 1
    pos_hint: {'y': .75, 'center_x': .5}
    height: '30dp'
    # Double .parent because dropdown proxies add_widget to container
    on_release: self.parent.parent.select(self.text)
''')


class FilterDD(F.DropDown):
    ignore_case = F.BooleanProperty(True)

    def __init__(self, **kwargs):
        self._needle = None
        self._order = []
        self._widgets = {}
        super(FilterDD, self).__init__(**kwargs)

    options = F.ListProperty()

    def on_options(self, instance, values):
        _order = self._order
        _widgets = self._widgets
        changed = False
        for txt in values:
            if txt not in _widgets:
                _widgets[txt] = btn = F.DDButton(text=txt)
                _order.append(txt)
                changed = True
        for txt in _order[:]:
            if txt not in values:
                _order.remove(txt)
                del _widgets[txt]
                changed = True
        if changed:
            self.apply_filter(self._needle)

    def apply_filter(self, needle):
        self._needle = needle
        self.clear_widgets()
        _widgets = self._widgets
        add_widget = self.add_widget
        ign = self.ignore_case
        _lcn = needle and needle.lower()
        for haystack in self._order:
            _lch = haystack.lower()
            if not needle or ((ign and _lcn in _lch) or
                              (not ign and needle in haystack)):
                add_widget(_widgets[haystack])


class FilterDDTrigger(F.BoxLayout):
    def __init__(self, **kwargs):
        super(FilterDDTrigger, self).__init__(**kwargs)
        self._prev_dd = None
        self._textinput = ti = F.TextInput(multiline=False)
        ti.bind(text=self._apply_filter)
        ti.bind(on_text_validate=self._on_enter)
        self._button = btn = F.Button(text=self.text)
        btn.bind(on_release=self._on_release)
        self.add_widget(btn)

    text = F.StringProperty('Number of Doses')

    def on_text(self, instance, value):
        self._button.text = value

    dropdown = F.ObjectProperty(None, allownone=True)

    def on_dropdown(self, instance, value):
        _prev_dd = self._prev_dd
        if value is _prev_dd:
            return
        if _prev_dd:
            _prev_dd.unbind(on_dismiss=self._on_dismiss)
            _prev_dd.unbind(on_select=self._on_select)
        if value:
            value.bind(on_dismiss=self._on_dismiss)
            value.bind(on_select=self._on_select)
        self._prev_dd = value

    def _apply_filter(self, instance, text):
        if self.dropdown:
            self.dropdown.apply_filter(text)

    def _on_release(self, *largs):
        if not self.dropdown:
            return
        self.remove_widget(self._button)
        self.add_widget(self._textinput)
        self.dropdown.open(self)
        self._textinput.focus = True

    def _on_dismiss(self, *largs):
        self.remove_widget(self._textinput)
        self.add_widget(self._button)
        self._textinput.text = ''

    def _on_select(self, instance, value):
        self.text = value

    def _on_enter(self, *largs):
        container = self.dropdown.container
        if container.children:
            self.dropdown.select(container.children[-1].text)
        else:
            self.dropdown.dismiss()


class Button(F.BoxLayout):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.submit = Button()
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)


class TopLabel(F.BoxLayout):
    def __init__(self, **kwargs):
        super(TopLabel, self).__init__(**kwargs)
        self.add_widget(Label(text='When will my Country be Vaccinated'))


runTouchApp(Builder.load_string('''
#:import F kivy.factory.Factory
#:import vaccineDate dataanalysis.vaccineDate

FloatLayout:
    BoxLayout:
        pos_hint: {'y': .75, 'center_x': .5}
        size_hint_x: 1
        FilterDDTrigger:
            id: dd1
            size_hint: 1, None
            dropdown:
                F.FilterDD(options=['2', '1'])
        FilterDDTrigger:
            id: dd2
            size_hint: 1, None
            text: 'Choose a country'
            dropdown: 
                F.FilterDD(options=['Israel', 'Chile', 'Slovenia', 'Portugal', 'Italy', \
                                    'Norway', 'Romania', 'Germany', 'Denmark', 'Austria', \
                                    'Belgium','Mexico','France','Lithuania','United States',\
                                    'Bulgaria','Slovakia','Canada','United Arab Emirates',\
                                    'Greece','United Kingdom'])   
    BoxLayout:
        pos_hint: {'y': 0.87, 'center_x': .5}
        size_hint_x: 1
        TopLabel:
            size_hint: 1, None
    Button:
        text: "Show" 
        size_hint_y: None
        height: 50
        size_hint_x: 1
        pos_hint: {'y': .70, 'center_x': .5} 
        on_release: 
            vaccineDate(dd2.text, dd1.text)
            graphBox.clear_widgets()
            graphBox.add_widget(F.Image(source='country.png'))

    BoxLayout:
        id: graphBox
        size_hint: 1 , .50
        pos_hint:{'y': .1, 'center_x': .5} 

'''))

