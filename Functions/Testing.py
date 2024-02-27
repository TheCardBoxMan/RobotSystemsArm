class bull:
    def __init__(self):
        self.bullshit = 0
    def read(self):
        print(self.bullshit)

    def morebull(self):
        self.bullshit =+ 1

if __name__ == '__main__':
    b =bull()
    b.read()
    b.morebull()
    b.read()
