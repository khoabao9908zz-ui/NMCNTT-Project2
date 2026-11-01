#include <iostream>
using namespace std;
int main(){
    int a;
    cin>>a;
    int product=a*10;
    
    while(product<100){
        cout<<"Enter number";
        cin>>a;
        product=a*10;
    }
    return 0;
}