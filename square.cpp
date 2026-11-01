#include <iostream>
using namespace std;

int main(){
      int a;

      do {
            cin >> a;
      } while(a < 1 || a > 15);

      for(int i = 1; i <= a; i++){
            for(int j = 1; j <= a; j++){
                  cout << "X";
            }
            cout << endl;
      }
      return 0;
}