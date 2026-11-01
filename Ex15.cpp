#include <iostream>
#include<cmath>
using namespace std;

    bool namnhuan(int year){
        return (year%4==0 && year%100!=0) ||(year%400==0);
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




    long long doingay(int year,int month,int day){
        long long totaldays=day;
        for(int y=1; y<year;y++){
            if(namnhuan(y)){
                totaldays+=366;
            }
            else{
                totaldays+=365;
            }
        }
        for(int m=1;m<month;m++){
            totaldays+=daysinmonth(m, year);
        }
        return totaldays;

    }
    int main(){
        int y1,m1,d1,y2,m2,d2;
        char c;
        cin>>y1>>c>>m1>>c>>d1>>y2>>c>>m2>>c>>d2;
        long long days1= doingay(y1,m1,d1);
        long long days2= doingay(y2,m2,d2);
        long long result=abs(days1-days2);
        cout<<"Days between: "<<result;

    return 0;
    }