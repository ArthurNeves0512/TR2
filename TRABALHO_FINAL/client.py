import fsm as fsm
import udp as udp
import argparse
import random

reciever = fsm.FSM()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server",type=str,default="137.131.178.229")
    parser.add_argument("--group",type=str,required=True)   
    parser.add_argument("--file",type=str,default="small")
    parser.add_argument("--protocol",type=str,default="saw",choices=["saw","gbn","sr"])  
    parser.add_argument("--window",type=int,default=1)             
    parser.add_argument("--loss",type=float,default=0.0)           
    parser.add_argument("--timeout",type=float,default=1.0)        
    parser.add_argument("--seed",type=int,default=None) 

    args = parser.parse_args()
    random.seed(args.seed)  # para tornar a perda simulada reproduzível

    try:
        reciever.execute(args.server,args.group,args.file,
                         args.protocol,args.window,args.loss,args.timeout)
    except Exception as e:

        print("lascou bahia",e)
        print(type(args.server))
        print(type(args.group))
        print(type(args.file))

if __name__ == "__main__":
    main()