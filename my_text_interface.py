import Tkinter as tk
import sys
import string
import Queue

class MyDialog:
    def __init__(self, parent):

        top = self.top = parent #tk.Toplevel(parent)

        self.entry_frame = tk.Frame(parent)
        tk.Label(self.entry_frame, text="Please enter English sentence:").pack()
        tk.Label(top, text="Example: move disk1 from pole1 to pole2").pack()
        tk.Label(top, text="Example: pick up disk1 from pole1").pack()
        tk.Label(top, text="Example: put down disk1 on pole2").pack()

        self.e = tk.Entry(self.entry_frame, width=100)
        self.e.pack(padx=15)

        self.entry_frame.pack(side=tk.TOP, fill=tk.BOTH)

        self.log_frame = tk.Frame(parent)
        self.text = tk.Text(self.log_frame)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll = tk.Scrollbar(self.log_frame)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(font="Courier 12", yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)

        self.log_frame.pack(side=tk.BOTTOM)

        self.fBottom = tk.Frame(top)

        c = tk.Button(self.fBottom, text="Close", command=self.close)
        c.pack(side = tk.RIGHT)

        b = tk.Button(self.fBottom, text="Execute", command=self.ok)
        b.pack(side = tk.RIGHT)
        self.value = ""

        c = tk.Button(self.fBottom, text="Parse", command=self.parse)
        c.pack(side = tk.RIGHT)

        self.fBottom.pack(side=tk.BOTTOM)

        #setup other stuff
        self.log_frame.bind('<<display-text>>', self.display_text_handler)

        self.message = Queue.Queue()

        self.parsed_plan = ""

        self.originalPlan = []
        self.plan = []


    def parse(self):
        if self.parsed_plan == "":
            self.value = self.e.get()
            #parse the plan
            self.parsed_plan = self.semantic_parser(self.value)
            self.log_info("{0} -> {1}".format(self.value, self.parsed_plan))
        else:
            self.log_error("Already parsed plan: {0}, cannot parse new plan.".format(self.parsed_plan))

    def get_noun_phrases_helper(self):

        endIndex = len(self.plan)
        begIndex = len(self.plan)

        if("and" in self.plan):
            endIndex = self.plan.index("and")
            begIndex = endIndex+1
        nounPhrase = self.plan[0:endIndex]

        self.plan = self.plan[begIndex:]
        self.log_info("done with noun phrases: ", str(self.plan))

        return nounPhrase

    def move_splitter(self, movePhrase):
        """
        Split a move action into a pick and put action and add it to self.plan
        """
        obj = movePhrase[1]
        toLocation = movePhrase[ movePhrase.index('to') + 1]
        fromLocation = movePhrase[ movePhrase.index('from') + 1]

        phrase = 'pick up ' + obj + ' from ' + fromLocation + ' and put ' + obj + ' on ' + toLocation
        if self.plan:
            self.plan = phrase.split(' ') + ['and'] + self.plan
        else:
            self.plan = phrase.split(' ') + self.plan

    def semantic_parser(self, plan):
            #Write code for simple semantic grammar here
            #Actions should be returned in the following format:
            #1. Mov Object Source Destination
            #2. Pick Object Source
            #3. Put Object Destination
        #But first, if for some reason the plan string is empty just exit
        if (len(plan) == 0):
            return plan

        plan = string.lower(plan).replace('left pole', 'pole1')
        plan = plan.replace('right pole', 'pole3')
        plan = plan.replace('middle pole', 'pole2')
        self.plan = string.split(plan) # A list of the words in the user command
        self.originalPlan = [w for w in plan]
        result = []

        # filter out 'it'
        objects = ['disk1', 'disk2', 'disk3']
        curObj = ''
        for i, elem in enumerate(self.plan):
            if elem in objects:
                curObj = elem
            if elem == 'it':
                self.plan[i] = curObj

		#The verb phrase should come first, so look at the first word
		#If the verb phase is present go ahead and parse the noun phrases
        self.log_info("Expanding sentence 'S' to VP1 NP1 NP3 NP4 | VP2 NP1 NP3 | VP3 NP1 NP4,")
        while(self.plan):
            self.log_info("about to parse words", str(self.plan))
            self.log_info("the identifying initial verb phrase...")
            if self.plan[0] == "mov" or self.plan[0] == "move":
                self.log_info("Case VP1 NP1 NP3 NP4 (\"Move\") found")
                self.log_info("Identifying noun phrases...")
                movePhrase = self.get_noun_phrases_helper()
                self.move_splitter(movePhrase)
            elif self.plan[0] == "pick":
                self.log_info("Case VP2 NP1 NP3 (\"Pick\") found.")
                self.log_info("Identifying noun phrases...")
                result.append("Pick " + self.get_noun_phrases())
            elif self.plan[0] == "put":
                self.log_info("Case VP3 NP1 NP4 (\"Put\") found.")
                self.log_info("Identifying noun phrases...")
                result.append("Put " + self.get_noun_phrases())
            else:
                self.log_error(self.plan, "Instructions must begin with Move, Pick or Put.")
                break
        if not result: return self.plan

        return result


    def get_noun_phrases(self):
        """
        Helper method. Given a string representing a plan,
        finds the noun phrases by removing every word other than "disk*" or "pole*.
		Does not check whether these are in the correct order."
        """

        result = ""
        #asssume that the noun phrases are in a fixed order
        #then just look for the keywords "disk" and "pole", ignoring everything else
        nounPhrase = self.get_noun_phrases_helper()

        for w in nounPhrase:
            if "disk" in w or "pole" in w:
                self.log_info("\"{0}\" found!".format(w))
                result += w.title() + " "
        return result

    def ok(self):
        if self.parsed_plan == "":
            self.parse()

        if (type(self.parsed_plan) == list):
    	    for command_string in self.parsed_plan:
    	        print command_string
    	else:
    	    print self.parsed_plan
    	self.top.destroy()

    def close(self):
    	self.value = "close"
    	print self.value
    	self.top.destroy()

    def log_info(self, printable_object, message=""):
        s = "[INFO]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')

    def log_error(self, printable_object, message=""):
        s =  "[ERROR]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')

    def display_text_handler(self, event=None):
        s = self.message.get()
        self.text.insert(tk.END, s)
        self.text.insert(tk.END, '\n')
        self.text.yview(tk.END)



def main():
    root = tk.Tk()
    root.title('Enter Command')
    d = MyDialog(root)
    root.wait_window(d.top)


if __name__ == "__main__":
        main()
