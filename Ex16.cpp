#include <iostream>
using namespace std;

    bool namnhuan(int year){
        return (year%4==0 && year%100!=0)|| (year%400==0);
    }

    int daysinmonth(int month, int year){
        if (month==2){
            if(namnhuan(year)){
                return 29;
            }
            else {
                return 28;
            }
        }
        if (month==4 ||month==6||month==9||month==11){
            return 30;
        }
        else{
            return 31;
        }
    }

    int main(){
        int y,m,d,n;
        char dash;
        cin>>y>>dash>>m>>dash>>d>>n;
        
        while(n>0){
            d++;
            if(d >daysinmonth(m,y)){
                d=1;
                m++;
            }
            if(m>12){
                m=1;
                y++;
            }
            n--;
        }
        while(n<0){
            d--;
            if(d<1){
                m--;
                if(m<1){
                    m=12;
                    y--;
                }
                d= daysinmonth(m,y);
            }
            n++;
        }
        
        cout<<"New date: "<<y<<dash;
        if(m<10){
            cout<<"0"<<m<<dash;
        }
        else{cout<<m<<dash;}

        if(d<10){
            cout<<"0"<<d;
        }
        else{cout<<d;}
 
    return 0;
}