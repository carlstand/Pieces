__author__ = 'ezikche'
import random
import kivy.metrics  
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.uix.label import Label

def visible(el):
    return visibleSource(el) or visibleTarget(el)

def visibleTarget(el):
    return isinstance(el, TargetSubElement) or isinstance(el, TargetElement)

def availableTarget(el):
    return visibleTarget(el) and not el.magneted

def visibleSource(el):
    return isinstance(el, SourceSubElement) or isinstance(el, SourceElement)

def isTouchedOrNotMoving(el):
    return el.touched or el.center_x > Window.width*2/3.0

class BaseSquareElement(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(-1)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    touched = BooleanProperty(False)

    def move(self):
        if(not self.touched):
            self.pos = Vector(*self.velocity) + self.pos

    def setVelocity(self, velocity_y):
        self.velocity_y = -1 * velocity_y

    def getVelocity():
        return velocity_y

class InvisibleElement(BaseSquareElement):
    def isMagneted(self, widget):
        return False

class SourceSubElement(BaseSquareElement):
    pass

class TargetSubElement(BaseSquareElement):
    magneted = BooleanProperty(False)

    def isMagneted(self, widget):
        distance = Vector(widget.pos).distance(self.pos)
        if distance < (self.width / 2.0):
            return True
        else:
            return False

    def setDarkColor(self):
        with self.canvas:
            Color(1, 1, 0, 0.5)

    def setBrightColor(self):
        with self.canvas:
            Color(1, 1, 0, 1)

    def markMagneted(self, mark):
        self.magneted = mark

    def paint(self):
        if self.magneted:
            self.setDarkColor()
        else:
            self.setBrightColor()

class TargetElement(GridLayout):
        
    def init(self, number):
        for i in range(1,number*number):
            if (random.randint(0,5) > 1):
                self.add_widget(TargetSubElement())
            else:
                self.add_widget(InvisibleElement())
        print len(filter(visibleTarget, self.children))
        if len(filter(visibleTarget, self.children)) == 0:
            self.add_widget(TargetSubElement())

    def markMagneted(self, SourceGroup):
        for targetChild in filter(visibleTarget, self.children):
            magneted = False
            for Source in filter(visibleSource, SourceGroup.children):
                if isTouchedOrNotMoving(Source):
                    v = Vector(0,0)
                    for sourceChild in Source.children:
                        if targetChild.isMagneted(sourceChild):
                            magneted = True
                            v = Vector(targetChild.pos) - Vector(sourceChild.pos)
                            # sourceChild.pos = targetChild.pos
                            break
                    #         print "target pos: " + str(targetChild.center)
                    #         print "source pos: " + str(sourceChild.center)
                    #         print "Vector : " + str(v)
                    if magneted:
                        # print "before: {}".format(Source.pos)
                        Source.pos = Vector(Source.pos) + v/3.0
                        # print "after: {}".format(Source.pos)
            targetChild.markMagneted(magneted)

    def paint(self):
        for targetChild in filter(visibleTarget, self.children):
            targetChild.paint()

class SourceElement(GridLayout):
    touched = BooleanProperty(False)

    def init(self, number):
        velocity = random.randint(1,5)
        for i in range(number):
            el = SourceSubElement()
            el.setVelocity(velocity)
            self.add_widget(el)

    def move(self):
        if self.center_x <= Window.width*2/3 :
            for child in self.children:
                child.move()

    def on_touch_up(self, touch):
        self.touched = False

    def on_touch_down(self, touch):
        for child in self.children:
            if child.collide_point(touch.x, touch.y):
                self.touched = True
                break

    def on_touch_move(self, touch):
        if self.touched:
            self.center = (touch.x, touch.y)   

class PiecesGame(Widget):
    target = ObjectProperty(None)
    score = ObjectProperty(None)

    def addLabel(self):
        self.score = Label()
        self.score.font_size =  kivy.metrics.sp(40)
        self.score.center_x = Window.width * 5 / 6
        self.score.top = Window.height -  kivy.metrics.sp(40)
        self.score.text = str('0%')
        self.add_widget(self.score, index = 0)

    def targetElementGenerate(self):
        r = random.randint(5,10)
        self.target = TargetElement(rows = r)
        self.target.init(random.randint(1,r))
        self.target.center = (Window.width * 5 / 6, Window.height / 2)
        self.add_widget(self.target, index = 0)

    def sourceElementGenerate(self, dt):
        sourceElement1 = SourceElement(rows = random.randint(1,5))
        sourceElement1.init(random.randint(2,5))
        sourceElement1.center = (Window.width*random.randint(1,8)/12,Window.height)
        self.add_widget(sourceElement1)
        # print len(filter(visibleSource, self.children))

    def update(self, dt):
        for widget in filter(visibleSource, self.children):
            widget.move()
            for child in widget.children:
                if(child.center_y < 0):
                    self.remove_widget(widget)
                    Window.remove_widget(widget)
                    widget.clear_widgets()
        self.target.markMagneted(self)
        self.target.paint()
        i = 0
        total = len(filter(visibleTarget, self.target.children))
        for widget in filter(visibleTarget, self.target.children):
            if widget.magneted:
                i += 1
        self.score.text = str(100*i/total) + "%"

    def on_touch_down(self, touch):
        for widget in filter(visibleSource, self.children):
            widget.on_touch_down(touch)

    def on_touch_up(self, touch):
        for widget in filter(visibleSource, self.children):
            widget.on_touch_up(touch)  
        if str(self.score.text) == '100%':
            print "game over"
            self.remove_widget(self.target)
            self.clear_widgets()
            self.addLabel()
            self.targetElementGenerate()

    def on_touch_move(self, touch):
        for widget in filter(visibleSource, self.children):
            widget.on_touch_move(touch)


class PiecesApp(App):
    def build(self):
        game = PiecesGame()
        game.addLabel()
        game.targetElementGenerate()
        Clock.schedule_interval(game.sourceElementGenerate, 5.0)
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PiecesApp().run()