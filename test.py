

def a(b):
    if b==1:
        print('ok')
    elif b==2:
        print('ok2')
        a(b-1)
    else:
        print('ok3')

a(2)