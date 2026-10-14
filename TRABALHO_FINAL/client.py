import fsm as fsm
import udp as udp
import argparse

reciever = fsm.FSM()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server",type=str,default="137.131.178.229")
    parser.add_argument("--group",type=str,default="grupo09")
    parser.add_argument("--file",type=str,default="small")

    args = parser.parse_args()

    try:
        reciever.execute(args.server,args.group,args.file)
    except Exception as e:

        print("lascou bahia",e)
        print(type(args.server))
        print(type(args.group))
        print(type(args.file))

if __name__ == "__main__":
    main() 

