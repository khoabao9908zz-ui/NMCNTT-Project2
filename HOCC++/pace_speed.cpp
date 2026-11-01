#include <iostream>
#include <iomanip>
using namespace std;
int main() {
double km, h, m, s;
cin >> km >> h >> m >> s;
double pace = (h*60 + m + s/60) /km;
double speed = km / (h + m/60 + s/3600);
cout << fixed << setprecision(2) << pace <<" "<<  fixed << setprecision(2) << speed << endl;
return 0;
}