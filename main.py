import kivy
#This Software is licensed under the MIT License. More information on LICENSE.txt.

kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.core.audio import SoundLoader
import os
import json
import datetime
import tkinter


MOBILE_VERSION = False
if not MOBILE_VERSION :
    import matplotlib.pyplot as plt
    from matplotlib import style
SOUND = True
error_sound = SoundLoader.load('error.wav')

def play_sound():
    if SOUND :
        error_sound.play()

        

#JSON
class MarksJson():
    json_file = 'Marks.json'
    with open(json_file, 'r+') as jfile :
        store = json.loads(jfile.read())

    def add_subject(self, subject, teacher, comments):
        self.store[subject] = { 'info':{
                                'teacher': teacher,
                                'comments': comments}
                                ,'marks':{
                                '1': {},
                                '2': {},
                                '3': {}
                               }}
        self.save_json()

    def add_marks(self, subject, mark, value, desc, grouped, trim, date):
        self.store[subject]['marks'][trim][str(desc)] = {'value': value,
                                                        'grouped': grouped,
                                                        'date': date,
                                                        'mark': []}
        for i in range(value):
            self.store[subject]['marks'][trim][str(desc)]['mark'].append(mark)

        self.save_json()

    def save_json(self):
        with open(self.json_file, 'w') as jfile :
            jfile.truncate()
            jfile.write(json.dumps(self.store))

    def del_json_subject(self, key):
        try :
            del self.store[key]
            self.save_json()
        except :
            print('Incorrect Key')

    def del_json_mark(self, trim, key, subject):
        del self.store[subject]['marks'][trim][key]
        self.save_json()

    def check_exists(self, subject):
        if str(subject) in self.store :
            return True
        else :
            return False

    def get_json(self):
        return self.store


class Average():
    json = MarksJson()

    def __init__(self):
        super(Average, self).__init__()
        self.store = self.json.get_json()

    def get_term_avg(self, subject, term):
        self.term = str(term)
        grouped_marks = []
        non_grouped_marks = []
        all_marks = [key for key in self.store[subject]['marks'][self.term]]
        for key in all_marks :
            mark = self.store[subject]['marks'][self.term][key]['mark'][0]
            value = self.store[subject]['marks'][self.term][key]['value']
            grouped = self.store[subject]['marks'][self.term][key]['grouped']

            if grouped :
                for k in range(value):
                    grouped_marks.append(float(mark))

            else :
                for k in range(value):
                    non_grouped_marks.append(float(mark))

        final_avg = self.calculate_avg(grouped=grouped_marks, non_grouped=non_grouped_marks)
        return final_avg

    def calculate_avg(self, grouped, non_grouped):
        # try :
        if len(grouped) == 0 and len(non_grouped) == 0 :
            final_avg = 0
        elif len(grouped) == 0 :
            final_avg = sum(non_grouped) / len(non_grouped)
        elif len(non_grouped) == 0 :
            final_avg = sum(grouped) / len(grouped)
        else :
            grouped_avg = sum(grouped) / len(grouped)
            non_grouped.append(grouped_avg)
            final_avg = sum(non_grouped) / len(non_grouped)

        return final_avg

    def get_term_marks(self, subject, term):
        all_marks = [key for key in self.store[subject]['marks'][str(term)]]
        term_marks = []
        for key in all_marks :
            term_marks.append(self.store[subject]['marks'][str(term)][key]['mark'][0])
        return term_marks

    def calculate_final_avg(self, term1, term2, term3):
        avgs = [i for i in [term1, term2, term3] if i > 0]
        try :
            return round(sum(avgs) / len(avgs), 2)
        except ZeroDivisionError :
            return 0        




#Placeholders
class SubjectButton(ListItemButton):

    avg = Average()
    json = MarksJson()

    def check_state(self, subject):
        if self.json.check_exists(subject) :
            self.term1 = self.avg.get_term_avg(subject=subject, term='1')
            self.term2 = self.avg.get_term_avg(subject=subject, term='2')
            self.term3 = self.avg.get_term_avg(subject=subject, term='3')
            final_avg = self.avg.calculate_final_avg(self.term1, self.term2, self.term3)
            if final_avg > 6 :
                return [0, 1, 0, 1]
            elif 0 < final_avg < 6 :
                return [1, 0, 0, 1]
            elif final_avg == -1 :
                return [0, 0, 1, 1]
        return [0, 0, 1, 1]



class MarksButton(ListItemButton):
    pass


class DisplaySubjectsPopup(Popup):
    name_input = ObjectProperty()
    teacher_input = ObjectProperty()
    comments_input = ObjectProperty()
    json = MarksJson()

    def retrieve_subject_data(self):
        subject_data = {'name': str(self.name_input.text),
                        'teacher': str(self.teacher_input.text),
                        'comments': str(self.comments_input.text)}

        for i in subject_data.values() :
            if len(str(i)) ==  0 :
                play_sound()
                return

        self.json.add_subject(subject=subject_data['name'], teacher=subject_data['teacher'],
                                comments=subject_data['comments'])


class PopupHelp(Popup):
    pass


class PopupInfo(Popup):
    json = MarksJson()
    store = MarksJson().get_json()
    name = ObjectProperty()
    teacher = ObjectProperty()
    comments = ObjectProperty()

    def __init__(self, key):
        super(PopupInfo, self).__init__()
        self.name.text = "Name : {}".format(str(key))
        self.teacher.text = "Teacher: {}".format(
        str(self.store[key]['info']['teacher']))
        self.comments.text = "Comments : {}".format(
        str(self.store[key]['info']['comments']))


class AddMarksPopup(Popup):

    json = MarksJson()
    mark_input = ObjectProperty()
    value_input = ObjectProperty()
    description_input = ObjectProperty()
    grouped_input = ObjectProperty()
    date_input = ObjectProperty()
    trim1_input = ObjectProperty()
    trim2_input = ObjectProperty()
    trim3_input = ObjectProperty()

    def __init__(self, current_subject, **kwargs):
        super(AddMarksPopup, self).__init__(**kwargs)
        self.subject = current_subject

    def retrieve_marks_data(self):
        if self.trim1_input.active : self.trimester = "1" #Tried loops and list comps ended up with this.
        elif self.trim2_input.active : self.trimester = "2"
        else : self.trimester = "3"
        marks_data = {  'mark': self.mark_input.text,
                        'value': self.value_input.value,
                        'description': self.description_input.text,
                        'grouped': self.grouped_input.active,
                        'trimester': self.trimester,
                        'date': self.date_input.text}

        for i in marks_data.values() :
            if len(str(i)) == 0 :
                play_sound()
                return

        self.json.add_marks(subject=self.subject, mark=marks_data['mark'], value=marks_data['value'],
                            desc=marks_data['description'], grouped=marks_data['grouped'],
                            trim=marks_data['trimester'], date=marks_data['date'])

    def get_date(self):
        i = datetime.datetime.now()
        return "{}/{}/{}".format(i.day, i.month, i.year)


class MarkInfoPopup(Popup):

    json = MarksJson()
    store = json.get_json()
    description = ObjectProperty()
    mark = ObjectProperty()
    date = ObjectProperty()
    trim = ObjectProperty()
    value = ObjectProperty()
    grouped = ObjectProperty()

    def __init__(self, current_subject, key, trim):
        super(MarkInfoPopup, self).__init__()
        self.subject = current_subject
        self.key = str(key.split('-')[0].strip())
        self.description.text = 'Description: {}'.format(self.key)
        self.mark.text = 'Mark: {}'.format(
                    self.store[self.subject]['marks'][trim][self.key]['mark'][0])
        self.date.text = 'Date: {}'.format(
                    self.store[self.subject]['marks'][trim][self.key]['date'])
        self.trim.text = 'Trimester: {}'.format(str(trim))
        self.value.text = 'Value: {}'.format(
            self.store[self.subject]['marks'][trim][self.key]['value'])
        self.grouped.text = 'Grouped: {}'.format(
            self.store[self.subject]['marks'][trim][self.key]['grouped'])


class MobilePopup(Popup):
    pass




#Screens
class DisplaySubjects(BoxLayout):
    subject_list_view = ObjectProperty()
    json = MarksJson()
    avg = Average()
    file_name = 'graph.png'

    def __init__(self, **kwargs):
        super(DisplaySubjects, self).__init__(**kwargs)
        try :
            self.load_records()
        except :
            pass

    def load_records(self):
        self.subjects_loaded = [subject for subject in self.json.get_json()]
        self.list_view_subjects = [subject for subject in self.subject_list_view.adapter.data]
        for subject in self.subjects_loaded :
            if subject not in self.list_view_subjects :
                self.subject_list_view.adapter.data.extend([subject])
                self.subject_list_view._trigger_reset_populate()

    def delete_record(self):
        if self.subject_list_view.adapter.selection :
            selected = self.subject_list_view.adapter.selection[0].text
            self.subject_list_view.adapter.data.remove(selected)
            self.subject_list_view._trigger_reset_populate()
            self.json.del_json_subject(selected)
            self.json.save_json()
        else :
            play_sound()

    def show_marks_widget(self):
        try :
            if self.subject_list_view.adapter.selection :
                selected  = self.subject_list_view.adapter.selection[0].text
                self.clear_widgets()
                self.add_widget(DisplayMarks(selected))
            else:
                play_sound()
        except :
            play_sound()


    def show_stats_widget(self):
        if not MOBILE_VERSION :
            if self.subject_list_view.adapter.selection :
                selected = self.subject_list_view.adapter.selection[0].text
                graph = DisplayStats(selected)
                graph.show_graph()
            else :
                play_sound()
        else :
            self.open_mobile_popup()

    def open_add_popup(self):
        add_pop = DisplaySubjectsPopup()
        add_pop.open()

    def open_info_popup(self):
        if self.subject_list_view.adapter.selection :
            selected = self.subject_list_view.adapter.selection[0].text
            info_pop = PopupInfo(selected)
            info_pop.open()
        else:
            play_sound()    

    def open_mobile_popup(self):
        mob_pop = MobilePopup()
        mob_pop.open()



class DisplayMarks(BoxLayout):

    json = MarksJson()
    avg = Average()
    title = ObjectProperty()
    t1_list = ObjectProperty()
    t2_list = ObjectProperty()
    t3_list = ObjectProperty()
    t1_avg_input = ObjectProperty()
    t2_avg_input = ObjectProperty()
    t3_avg_input = ObjectProperty()
    final_avg_input = ObjectProperty()

    def __init__(self, subject, **kwargs):
        super(DisplayMarks, self).__init__(**kwargs)
        self.subject = subject
        self.title.text = "{} Marks".format(subject)
        self.update_avgs()
        self.store = self.json.get_json()
        self.call_load_method()

    def update_avgs(self):
        self.t1_avg = self.avg.get_term_avg(subject=self.subject, term='1')
        self.t2_avg = self.avg.get_term_avg(subject=self.subject, term='2')
        self.t3_avg = self.avg.get_term_avg(subject=self.subject, term='3')
        self.t1_avg_input.text = 'Avg: {}'.format('{0:.2f}'.format(self.t1_avg))
        self.t2_avg_input.text = 'Avg: {}'.format('{0:.2f}'.format(self.t2_avg))
        self.t3_avg_input.text = 'Avg: {}'.format('{0:.2f}'.format(self.t3_avg))
        final_avg = self.avg.calculate_final_avg(self.t1_avg, self.t2_avg, self.t3_avg)
        self.final_avg_input.text = 'Final Average: {}'.format(final_avg)

    def call_load_method(self):
        self.load_records(trimester='1', list_view=self.t1_list)
        self.load_records(trimester='2', list_view=self.t2_list)
        self.load_records(trimester='3', list_view=self.t3_list)

    def delete_mark(self):
        try :
            self.selection = self.check_selection()[0]
            self.key = str(self.selection.split('-')[0].strip())
            self.listview = self.check_selection()[2]
            self.listview.adapter.data.remove(self.selection)
            self.listview._trigger_reset_populate()
            self.json.del_json_mark(subject=self.subject, key=self.key, trim=self.check_selection()[1])
        except:
            play_sound()    

    def load_records(self, trimester, list_view):
        self.loaded_marks = [mark for mark in self.store[self.subject]['marks'][trimester]]
        self.list_view_marks = [mark for mark in list_view.adapter.data]
        for i in self.loaded_marks :
            if i not in str(self.list_view_marks) :
                list_view.adapter.data.extend(['{} - {}'.format(i, self.store[self.subject]['marks'][trimester][i]['mark'][0])])
                list_view._trigger_reset_populate()

    def check_selection(self):
        cond1 = self.t1_list.adapter.selection
        cond2 = self.t2_list.adapter.selection
        cond3 = self.t3_list.adapter.selection
        if cond1 :
            self.selected = self.t1_list.adapter.selection[0].text
            self.trimester = '1'
            self.listview = self.t1_list
        elif cond2 :
            self.selected = self.t2_list.adapter.selection[0].text
            self.trimester = '2'
            self.listview = self.t2_list
        elif cond3 :
            self.selected = self.t3_list.adapter.selection[0].text
            self.trimester = '3'
            self.listview = self.t3_list
        return self.selected, self.trimester, self.listview

    def open_add_marks_popup(self):
        add_marks_popup = AddMarksPopup(self.subject)
        add_marks_popup.open()

    def open_marks_info_popup(self):
        try: 
            marks_info_popup = MarkInfoPopup(   current_subject=self.subject,
                                            key=self.check_selection()[0],
                                            trim=self.check_selection()[1])
            marks_info_popup.open()
        except:
            play_sound()    


class DisplayStats():

    avg = Average()

    def __init__(self, selected):
        super(DisplayStats, self).__init__()
        self.subject = selected
        self.create_graph()

    def create_graph(self):
        plt.rcParams["figure.figsize"] = (10, 8)
        term1_y = self.avg.get_term_marks(subject=self.subject, term='1')
        term1_x = [i[0] + 1 for i in enumerate(term1_y)]
        term2_y = self.avg.get_term_marks(subject=self.subject, term='2')
        term2_x = [i[0] + 1 for i in enumerate(term2_y)]
        term3_y = self.avg.get_term_marks(subject=self.subject, term='3')
        term3_x = [i[0] + 1 for i in enumerate(term3_y)]

        style.use('fivethirtyeight')

        plt.scatter(term1_x, term1_y, color='k', s=80)
        plt.plot(term1_x, term1_y, label='Term 1', color='k', linewidth=3)
        plt.scatter(term2_x, term2_y, color='r', s=80)
        plt.plot(term2_x, term2_y, label='Term 2', color='r', linewidth=3)
        plt.scatter(term3_x, term3_y, color='g', s=80)
        plt.plot(term3_x, term3_y, label='Term 3', color='g', linewidth=3)
        plt.xlabel('Amount')
        plt.ylabel('Mark')
        plt.title(self.subject)
        plt.legend()
        plt.ylim((1, 10))
        plt.xlim((0, 8))

    def show_graph(self):
        plt.show()

#Root
class MarksRoot(BoxLayout):

    def show_subjects_widget(self):
        widget = DisplaySubjects()
        self.clear_widgets()
        self.add_widget(widget)

    def open_help_popup(self):
        help_pop = PopupHelp()
        help_pop.open()    

    


class MarksApp(App):
    def build(self):
        return MarksRoot()        


if __name__ == '__main__' :
    app = MarksApp()
    app.run()

