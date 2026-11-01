#include <iostream>
#include <string>

using namespace std;

int main() {
    string s;
    cin >> s;

    int count[26] = {};
    for (char color : s) {
        ++count[color - 'A'];
    }

    int odd = 0;
    for (int frequency : count) {
        odd += frequency % 2;
    }

    cout << odd / 2 << '\n';
    return 0;
}
