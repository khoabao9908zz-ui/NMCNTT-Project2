#include <iostream>
using namespace std;
long long demchuso(long long number){
    if(number==0 ||number==1){
        return 1;
    }
    int count=0;
    while(number>0){
        count++;
        number/=10;
    }
    return count;
}
void kiemtraX(int n){
    cout<<"X=[";
    bool first =true;
    long long giaithua=1;
    int x=0;
    while(true){
        
        if(x>0){
        giaithua*=x;
        }
    
        int demso=demchuso(giaithua);
        if(demso==n){
            if(!first){
                cout<<", ";
            }
            cout<<x;
            first=false;
        }
        if(demso>n){
            break;
        }
        x++;

    }
    cout<<"]";
}   
int main(){
    int n;
    cin>>n;
    kiemtraX(n);
    return 0;
}