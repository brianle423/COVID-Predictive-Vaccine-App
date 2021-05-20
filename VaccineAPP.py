#######################################################################################################################
#
#   Description:
#   This code is an app that shows a prediction model graph of when a country might be 100% vaccinated.
#   You can choose a country and how many doses you want to see.
#
#######################################################################################################################

#Importing the kivy modules that we need for this
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image


#This segment Builds the Two Buttons and dropdown options
Builder.load_string('''
<MainDDButton@Button>:
    background_normal: ''
    background_color: 0.306, 0.627, 0.82, 1 
    border: 10, 10, 10, 10
    font_size: '20sp'
    size_hint_y: None
    size_hint_x: 1
    canvas.before:
        Color:
            rgba: 0.204, 0.58, 0.796, 1
        Line:
            width: 5
            rectangle: self.x, self.y, self.width, self.height
<DDButton@Button>:
    background_normal: ''
    background_color: 0.286, 0.467, 0.675, 1
    font_size: '17sp'
    size_hint_y: None
    size_hint_x: 1
    pos_hint: {'y': .75, 'center_x': .5}
    height: '30dp'
    canvas.before:
        Color:
            rgba: 0.239, 0.388, 0.561, 1
        Line:
            width: 3
            rectangle: self.x, self.y, self.width, self.height
    # Double .parent because dropdown proxies add_widget to container
    on_release: self.parent.parent.select(self.text)
''')

#This Class makes the dropdowns
class FilterDD(F.DropDown):
    ignore_case = F.BooleanProperty(True)

    def __init__(self, **kwargs):
        self._needle = None
        self._order = []
        self._widgets = {}
        super(FilterDD, self).__init__(**kwargs)


    options = F.ListProperty()

    #This function puts the options on the dropdown
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

    #This applies the filter when you search for your country in the dropdown so you can find it faster
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

#This class has all of the triggers for the Dropdown
class FilterDDTrigger(F.BoxLayout):
    def __init__(self, **kwargs):
        super(FilterDDTrigger, self).__init__(**kwargs)
        self._prev_dd = None
        self._textinput = ti = F.TextInput(multiline=False)
        ti.bind(text=self._apply_filter)
        ti.bind(on_text_validate=self._on_enter)
        self._button = btn = F.MainDDButton(text=self.text)
        btn.bind(on_release=self._on_release)
        self.add_widget(btn)

    text = F.StringProperty('Number of Doses')

    #This function makes it so the text on the button holding the value
    def on_text(self, instance, value):
        self._button.text = value

    dropdown = F.ObjectProperty(None, allownone=True)

    #This function defines what happens to the previously selected options in the dropdowns
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

    #Applies a filter to the dropdown so you can find the country you are looking for faster
    def _apply_filter(self, instance, text):
        if self.dropdown:
            self.dropdown.apply_filter(text)

    #Defines what happens after you release and choose an option
    def _on_release(self, *largs):
        if not self.dropdown:
            return
        self.remove_widget(self._button)
        self.add_widget(self._textinput)
        self.dropdown.open(self)
        self._textinput.focus = True

    #Defines what happens when you don't choose an option after opening the dropdown
    def _on_dismiss(self, *largs):
        self.remove_widget(self._textinput)
        self.add_widget(self._button)
        self._textinput.text = ''

    #Defines a function on what happens to the dropdown when you click on the dropdown option
    def _on_select(self, instance, value):
        self.text = value

    #Defines a function on what happens to the dropdown when you press enter on the keyboard after searching for an item in the list
    def _on_enter(self, *largs):
        container = self.dropdown.container
        if container.children:
            self.dropdown.select(container.children[-1].text)
        else:
            self.dropdown.dismiss()

#This is the class for the Submit button
class Button(F.BoxLayout):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.submit = Button()
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

#Top Header for the app
class TopLabel(F.BoxLayout):
    def __init__(self, **kwargs):
        super(TopLabel, self).__init__(**kwargs)
        self.add_widget(Label(text='When Will My Country be Vaccinated?', font_size='30sp'))

#Place holder image for when the app is just started and the area is empty
class GraphPNG(F.BoxLayout):
    def __init__(self, **kwargs):
        super(GraphPNG, self).__init__(**kwargs)
        self.add_widget(Image(source='worldmap.png'))

#Building the whole app
runTouchApp(Builder.load_string('''
#:import F kivy.factory.Factory

#Importing a function from another file to use in the app
#:import vaccineDate dataanalysis.vaccineDate

FloatLayout:
    
    #Changing the color of the whole app
    canvas:
        Color:
            rgb: 0.337, 0.784, 0.769, 1
        Rectangle:
            size: self.size
    
    #Making a box to put the two dropdowns in 
    BoxLayout:
        pos_hint: {'y': .75, 'center_x': .5}
        size_hint_x: 1
        text_size: self.size
        
        #Putting Both the dropdowns in the box
        FilterDDTrigger:
            id: doses
            size_hint: 1, None
            dropdown:
                F.FilterDD(options=['2', '1'])
        FilterDDTrigger:
            id: country
            size_hint: 1, None
            text: 'Choose a country'
            dropdown: 
                F.FilterDD(options=['Israel', 'Chile', 'Slovenia', 'Portugal', 'Italy', \
                                    'Norway', 'Romania', 'Germany', 'Denmark', 'Austria', \
                                    'Belgium','Mexico','France','Lithuania','United States',\
                                    'Bulgaria','Slovakia','Canada','United Arab Emirates',\
                                    'Greece','United Kingdom','India','Uzbekistan','Indonesia',\
                                    'Pakistan','Brazil','Bangladesh','Russia','Mexico',\
                                    'Japan','Philippines','Vietnam','Turkey','Iran','Thailand',\
                                    ])  
    
    #Making a BoxLayout to place the top label at the top 
    BoxLayout:
        pos_hint: {'y': 0.87, 'center_x': .5}
        size_hint_x: 1
        TopLabel:
            size_hint: 1, None 
            
    #Showing the Show button on screen  
    Button:
        text: "Show" 
        font_size: '20sp'
        size_hint_y: None
        height: 50
        size_hint_x: 1
        background_normal: ''
        background_color: 0.212, 0.337, 0.486, 1
        pos_hint: {'y': .70, 'center_x': .5} 
        
        #saying what the submit button does on press
        on_release: 
            graphBox.clear_widgets()
            vaccineDate(country.text, doses.text)
            graphBox.add_widget(F.Image(source='{country}-{doses}.png'.format(country=country.text, doses=doses.text)))
    
    #Making a BoxLayout for where the prediction graphs will go 
    BoxLayout:
        size_hint: 1 , .69
        pos_hint:{'y': 0.005, 'center_x': .5} 
        GraphPNG:
            id: graphBox 
            pos_hint: {'y': 0.005, 'center_x': .5}

'''))