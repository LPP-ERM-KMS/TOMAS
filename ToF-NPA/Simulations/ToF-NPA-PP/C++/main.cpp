#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <fstream>

using namespace std;

double RandomNumberGenerator(double start, double end) {
    random_device dev;
    mt19937 rng(dev());
    uniform_real_distribution<double> dist(start, end);
    return dist(rng);
}

void GenerateGasParticle(double* x, double* y, double* z) {
    double v1, v2, rsquared;
    do {
        v1 = RandomNumberGenerator(-1, 1);
        v2 = RandomNumberGenerator(-1, 1);
        rsquared = v1 * v1 + v2 * v2;
    } while (rsquared >= 1);

    double r = sqrt(rsquared) * 0.035; // m
    *x = r * (v1 * v1 - v2 * v2) / rsquared;
    *y = r * 2 * (v1 * v2) / rsquared;
    *z = RandomNumberGenerator(0, 1) * 3; // m
}

void GenerateGas(int AmountOfParticles, vector<vector<double>>& Gas) {
    cout << "Populating with a gas of " << AmountOfParticles << " particles:\n";

    for (int i = 0; i < AmountOfParticles; i++) {
        double xgas, ygas, zgas;
        GenerateGasParticle(&xgas, &ygas, &zgas);
        Gas.push_back({xgas, ygas, zgas});

        float progress = static_cast<float>(i + 1) / AmountOfParticles * 100.0;
        int barWidth = 70;
        int pos = barWidth * progress / 100.0;
        
        cout << "[";
        for (int j = 0; j < barWidth; ++j) {
            if (j < pos) cout << "=";
            else if (j == pos) cout << ">";
            else cout << " ";
        }
        cout << "] " << int(progress) << " %\r";
        cout.flush();
    }
    cout << endl;
}

bool CheckHit(double x, double y, double z, vector<vector<double>>& Gas) {
    // Add your logic to check for hits here
    return true;
}

int main() {
    double P = 1e-9; //bar
    double r = 0.035;
    double h = 3;
    int sections = 10000; //divy up in sections with prob P, total passing prob is then p**sections
    double V = M_PI * r * r * h / sections;
    double T = 300.0;
    int hits = 0, misses = 0;
    int AmountOfParticles = static_cast<int>(round((P / (8.314462 * T) * 6.02214076e23) * V));
    vector<vector<double>> Gas;
    GenerateGas(AmountOfParticles, Gas);

    ofstream outputhit("hit.txt");
    ofstream outputmiss("miss.txt");

    // Perform hit/miss checks and write to files
    for (int i = 0; i < Gas.size(); i++) {
        if (CheckHit(Gas[i][0], Gas[i][1], Gas[i][2], Gas)) {
            outputhit << Gas[i][0] << " " << Gas[i][1] << " " << Gas[i][2] << endl;
            hits++;
        } else {
            outputmiss << Gas[i][0] << " " << Gas[i][1] << " " << Gas[i][2] << endl;
            misses++;
        }
    }

    outputhit.close();
    outputmiss.close();

    cout << "Hits: " << hits << endl;
    cout << "Misses: " << misses << endl;

    double PassingProbabilitySection = hits/misses;
    double PassingProbability = pow(PassingProbabilitySection,sections);

    cout << "Passing Probability: " << misses << endl;

    return 0;
}
