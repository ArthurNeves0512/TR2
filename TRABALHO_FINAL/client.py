import fsm as fsm
reciever = fsm.FSM()

def main():
    try:
        reciever.execute()
    except Exception as e:
        print("lascou bahia",e)

if __name__ == "__main__":
    main() 
