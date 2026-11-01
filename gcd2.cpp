#include <iostream>
#include<cmath>
using namespace std;
int main(){
    int a, b;
    cin>>a>>b;
    a=abs(a);
    b=abs(b);
    while(a!=b){
        if(a==0){
            a=b;
            break;
        }
        if(b==0){
            break;
        }
        if(a>b){
            a=a-b;
        }
        else { b = b-a;}
    }
    cout <<a<<endl;
    return 0;
}