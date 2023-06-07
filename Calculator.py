from tkinter import *

window = Tk()
window.title("Калькулятор")
window.geometry('380x365+100+100')
window["background"] = "black"


class Caltulator(Frame):
    def __init__(self, root):
        super(Caltulator, self).__init__(root)
        self.position()

# Логика действий
    def logic(self, event):
        if event == "DEL":
            self.formula = self.formula[0:-1]
        elif event == "C":
            self.formula = ""
        elif event == "=":
            self.formula = str(eval(self.formula))
        elif event == "(":
            self.formula += event
        elif event == ")":
            self.formula += event
        else:
            if self.formula == "0":
                self.formula = ""
            self.formula += event
        self.update()
    # None - 0
    def update(self):
        if self.formula == "":
            self.formula = "0"
        self.label.configure(text=self.formula)

# Кнопки
    def position(self):
        self.formula = "0"
        self.label = Label(text=self.formula, background="black", foreground="white")
        self.label.place(x=11, y=50)
        buttons = ["C", "/", "*", "DEL", "7", "8", "9", "-", "4", "5", "6", "+", "1", "2", "3", "=", "%", "0", ",", "(", ")"]
        # Расположение
        x = 10
        y = 100
        for btns in buttons:
            def position(da=btns):
                self.logic(da)
            if btns == ")":
                Button(text=")", background="white", command=position).place(x=325, y=300, width=45, height=50)
            elif btns == "(":
                Button(text="(", background="white", command=position).place(x=280, y=300, width=45, height=50)
            else:
                Button(text=btns, background="white", command=position).place(x=x, y=y, width=90, height=50)
                x += 90
                if x > 300:
                    x = 10
                    y += 50


app = Caltulator(window)
app.pack()
window.mainloop()