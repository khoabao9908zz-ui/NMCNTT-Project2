#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    int so;
    int soTruoc;
    int streak =0;
    int maxstreak =0;
    for (int i=1; i<=n;i++) {
        cin >> so;
        
        if (i==1) {
            streak = 1;
        }
            else if (so > soTruoc) {
                streak++;
            }
            else { streak = 1; }

            if (streak > maxstreak) {
                maxstreak = streak;
            }
           
        soTruoc = so;
    }
    cout << maxstreak << endl;
    return 0;
}
