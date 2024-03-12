using namespace std;
#include <numeric>
#include <random>
#include <cmath>
#include <iostream>
#include <vector>
#include <fstream>

double RandomNumberGenerator(double start, double end) {
    random_device dev;
    mt19937 rng(dev());
    uniform_real_distribution<double> dist(start, end);
    double RandomNumber = dist(rng);
    return RandomNumber;
}

void GenerateDirection(double* x, double* y, double* z) {
    double phi = RandomNumberGenerator(0, 2 * M_PI);
    double theta = acos(1 - 2 * RandomNumberGenerator(0, 1));
    *x = sin(theta) * cos(phi);
    *y = sin(theta) * sin(phi);
    *z = cos(theta);
}

void GenerateOrigin(double* x, double* y, double* z) {
    double v1, v2, rsquared;
    do {
        v1 = RandomNumberGenerator(-1, 1);
        v2 = RandomNumberGenerator(-1, 1);
        rsquared = v1 * v1 + v2 * v2;
    } while (rsquared >= 1);

    double r = sqrt(rsquared) * 35; // mm
    *x = r * (v1 * v1 - v2 * v2) / rsquared;
    *y = r * 2 * (v1 * v2) / rsquared;
    *z = 0;
}

void GenerateGasParticle(double* x, double* y, double* z) {
    double v1, v2, rsquared;
    do {
        v1 = RandomNumberGenerator(-1, 1);
        v2 = RandomNumberGenerator(-1, 1);
        rsquared = v1 * v1 + v2 * v2;
    } while (rsquared >= 1);

    double r = sqrt(rsquared) * 35; // mm
    *x = r * (v1 * v1 - v2 * v2) / rsquared;
    *y = r * 2 * (v1 * v2) / rsquared;
    *z = RandomNumberGenerator(0, 1) * 300; // mm
}

void GenerateGas(int AmountOfParticles, vector<vector<double>>& Gas) {
    cout << "Populating with a gas, ";
    for (int i = 0; i < AmountOfParticles; i++) {
        double percentage = i/AmountOfParticles;
        cout << percentage;
        cout << "% Done at";
        cout << "step ";
        cout << i;
        cout << "\n";
        double xgas, ygas, zgas;
        GenerateGasParticle(&xgas, &ygas, &zgas);
        Gas[i] = {xgas, ygas, zgas};
    }
}

bool CheckHit(double x, double y, double z, vector<vector<double>>& Gas) {
    // Add your logic to check for hits here
    return true;
}

int main() {
    double P = 1e-9;
    double V = 0.003675;
    double T = 300.0;
    double x_dir = 0, y_dir = 0, z_dir = 1;
    double x_pos = 0, y_pos = 0, z_pos = 0;
    int hits = 0, misses = 0;
    int AmountOfParticles = static_cast<int>(round((P / (8.314462 * T) * 6.02214076e23) * V));
    vector<vector<double>> Gas(AmountOfParticles);
    GenerateGas(AmountOfParticles, Gas);

    ofstream outputhit("hit.txt");
    ofstream outputmiss("miss.txt");

    // Perform hit/miss checks and write to files

    outputhit.close();
    outputmiss.close();

    return 0;
}
