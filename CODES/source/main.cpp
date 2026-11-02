#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <random>
#include <limits>
#include <iomanip>
#include <numeric>
#include <matplot/matplot.h>

using namespace std;

// The five strategies used in the simulation.
enum Move {
    COOPERATE,
    DEFECT
};

enum Strategy {
    TIT_FOR_TAT,
    GRIM_TRIGGER,
    ALWAYS_COOPERATE,
    ALWAYS_DEFECT,
    RANDOM
};

const int STRATEGY_COUNT = 5;

// Each strategy matchup is simulated this many times.
// Increase this for smoother averages, or reduce it for faster experiments.
const int MATCHUP_TRIALS = 100;

const vector<string> STRATEGY_NAMES = {
    "Tit for Tat",
    "Grim Trigger",
    "Always Cooperate",
    "Always Defect",
    "Random"
};

// Payoff matrix:
// C against C -> 3, 3
// C against D -> 0, 5
// D against C -> 5, 0
// D against D -> 0, 0
int payoff(Move myMove, Move opponentMove) {
    if (myMove == COOPERATE && opponentMove == COOPERATE) {
        return 3;
    }
    if (myMove == COOPERATE && opponentMove == DEFECT) {
        return 0;
    }
    if (myMove == DEFECT && opponentMove == COOPERATE) {
        return 5;
    }
    return 0;
}

bool randomEvent(double probability, mt19937& rng) {
    if (probability <= 0.0) return false;
    if (probability >= 1.0) return true;

    uniform_real_distribution<double> distribution(0.0, 1.0);
    return distribution(rng) < probability;
}

// Returns the strategy's intended move.
// forgiveness is the probability of responding with cooperation in the
// specific situations described below. Execution error is applied separately.
Move chooseMove(
    Strategy strategy,
    Move opponentPreviousMove,
    bool& grimTriggered,
    double forgiveness,
    mt19937& rng
) {
    if (strategy == ALWAYS_COOPERATE) {
        return COOPERATE;
    }

    if (strategy == ALWAYS_DEFECT) {
        return DEFECT;
    }

    if (strategy == TIT_FOR_TAT) {
        // TFT copies the opponent's previous executed move, but may forgive
        // a previous defection and cooperate instead.
        if (opponentPreviousMove == DEFECT &&
            randomEvent(forgiveness, rng)) {
            return COOPERATE;
        }
        return opponentPreviousMove;
    }

    if (strategy == GRIM_TRIGGER) {
        // Standard Grim Trigger defects forever after a defection.
        // With forgiveness enabled, it may reset its trigger and cooperate.
        if (grimTriggered) {
            if (randomEvent(forgiveness, rng)) {
                grimTriggered = false;
                return COOPERATE;
            }
            return DEFECT;
        }
        return COOPERATE;
    }

    // Random chooses C or D with equal probability.
    uniform_int_distribution<int> distribution(0, 1);
    return distribution(rng) == 0 ? COOPERATE : DEFECT;
}

struct GameResult {
    double player1Score;
    double player2Score;
};

// Plays one iterated game. errorRate is the probability that an intended
// move is flipped before it is actually played.
GameResult playGame(
    Strategy player1Strategy,
    Strategy player2Strategy,
    int rounds,
    double errorRate,
    double forgiveness,
    mt19937& rng
) {
    double player1Score = 0;
    double player2Score = 0;

    // Both players start by treating the opponent's previous move as C.
    Move player1PreviousMove = COOPERATE;
    Move player2PreviousMove = COOPERATE;

    // Each player's Grim Trigger state is specific to this opponent.
    bool player1GrimTriggered = false;
    bool player2GrimTriggered = false;

    for (int round = 0; round < rounds; round++) {
        Move player1Intended = chooseMove(
            player1Strategy, player2PreviousMove,
            player1GrimTriggered, forgiveness, rng
        );

        Move player2Intended = chooseMove(
            player2Strategy, player1PreviousMove,
            player2GrimTriggered, forgiveness, rng
        );

        // Execution errors flip intended moves into their opposite.
        Move player1Move = player1Intended;
        Move player2Move = player2Intended;

        if (randomEvent(errorRate, rng)) {
            player1Move = (player1Move == COOPERATE) ? DEFECT : COOPERATE;
        }
        if (randomEvent(errorRate, rng)) {
            player2Move = (player2Move == COOPERATE) ? DEFECT : COOPERATE;
        }

        player1Score += payoff(player1Move, player2Move);
        player2Score += payoff(player2Move, player1Move);

        // Update history using the moves that were actually executed.
        player1PreviousMove = player1Move;
        player2PreviousMove = player2Move;

        // A Grim Trigger player is triggered by an actual defection from
        // the opponent, not by the opponent's intended move.
        if (player2Move == DEFECT) {
            player1GrimTriggered = true;
        }
        if (player1Move == DEFECT) {
            player2GrimTriggered = true;
        }
    }

    return { player1Score, player2Score };
}

// Estimates average scores for a representative matchup, then multiplies
// those averages by the number of such pairs in the population.
// This avoids simulating every individual pair separately.
vector<double> executeGeneration(
    const vector<int>& population,
    int rounds,
    double errorRate,
    double forgiveness,
    mt19937& rng
) {
    vector<double> fitness(STRATEGY_COUNT, 0.0);

    for (int i = 0; i < STRATEGY_COUNT; i++) {
        for (int j = i; j < STRATEGY_COUNT; j++) {
            long long games;

            if (i == j) {
                games = 1LL * population[i] * (population[i] - 1) / 2;
            } else {
                games = 1LL * population[i] * population[j];
            }

            if (games == 0) {
                continue;
            }

            double totalScore1 = 0.0;
            double totalScore2 = 0.0;

            for (int trial = 0; trial < MATCHUP_TRIALS; trial++) {
                GameResult result = playGame(
                    static_cast<Strategy>(i),
                    static_cast<Strategy>(j),
                    rounds,
                    errorRate,
                    forgiveness,
                    rng
                );

                totalScore1 += result.player1Score;
                totalScore2 += result.player2Score;
            }

            double averageScore1 = totalScore1 / MATCHUP_TRIALS;
            double averageScore2 = totalScore2 / MATCHUP_TRIALS;

            fitness[i] += games * averageScore1;
            fitness[j] += games * averageScore2;
        }
    }

    return fitness;
}

// Evolves the population using a selection-intensity parameter alpha.
//
// alpha = 0: no selection; population composition stays unchanged.
// alpha = 1: proportional selection based on average accumulated payoff.
// Intermediate values soften the selection pressure.
//
// Integer counts are assigned with the largest-remainder method so the
// total population remains exactly constant.
vector<int> scalePopulation(
    const vector<double>& fitness,
    const vector<int>& population,
    double alpha
) {
    int totalPopulation = 0;
    for (int count : population) {
        totalPopulation += count;
    }

    vector<double> averageFitness(STRATEGY_COUNT, 0.0);

    for (int i = 0; i < STRATEGY_COUNT; i++) {
        if (population[i] > 0) {
            averageFitness[i] = fitness[i] / population[i];
        }
    }

    // Population-weighted mean payoff per individual.
    double meanFitness = 0.0;
    for (double value : fitness) {
        meanFitness += value;
    }
    meanFitness /= max(1, totalPopulation);

    // If no positive payoff was obtained, there is no usable selection
    // signal. Keep the population unchanged rather than dividing by zero.
    if (meanFitness <= 0.0 || !isfinite(meanFitness)) {
        return population;
    }

    vector<double> weights(STRATEGY_COUNT, 0.0);
    double totalWeight = 0.0;

    for (int i = 0; i < STRATEGY_COUNT; i++) {
        if (population[i] == 0) {
            continue;
        }

        double relativeFitness = averageFitness[i] / meanFitness;

        // Convex blend of neutral reproduction and payoff-based selection.
        // Since alpha is in [0,1] and relativeFitness is nonnegative,
        // the weight cannot become negative.
        double selectionFactor = (1.0 - alpha) + alpha * relativeFitness;

        weights[i] = population[i] * selectionFactor;
        totalWeight += weights[i];
    }

    if (totalWeight <= 0.0 || !isfinite(totalWeight)) {
        return population;
    }

    vector<int> newPopulation(STRATEGY_COUNT, 0);
    vector<double> fractionalRemainder(STRATEGY_COUNT, 0.0);

    int assigned = 0;

    for (int i = 0; i < STRATEGY_COUNT; i++) {
        double exactCount = totalPopulation * weights[i] / totalWeight;

        newPopulation[i] = static_cast<int>(floor(exactCount));
        fractionalRemainder[i] = exactCount - newPopulation[i];
        assigned += newPopulation[i];
    }

    int remaining = totalPopulation - assigned;

    // Award leftover individuals to the largest fractional remainders.
    while (remaining > 0) {
        int largest = -1;

        for (int i = 0; i < STRATEGY_COUNT; i++) {
            if (fractionalRemainder[i] < 0.0) {
                continue;
            }
            if (largest == -1 ||
                fractionalRemainder[i] > fractionalRemainder[largest]) {
                largest = i;
            }
        }

        // Defensive fallback; should not be needed with valid inputs.
        if (largest == -1) {
            largest = 0;
        }

        newPopulation[largest]++;
        fractionalRemainder[largest] = -1.0;
        remaining--;
    }

    return newPopulation;
}

void plotit(const vector<vector<int>>& populationHistory) {
    if (populationHistory.empty()) {
        cout << "No population history is available to plot.\n";
        return;
    }

    int totalPopulation = 0;
    for (int count : populationHistory[0]) {
        totalPopulation += count;
    }

    if (totalPopulation <= 0) {
        cout << "Cannot plot an empty population.\n";
        return;
    }

    vector<double> generations;
    vector<vector<double>> percentages(STRATEGY_COUNT);

    for (int generation = 0;
         generation < static_cast<int>(populationHistory.size());
         generation++) {
        generations.push_back(generation);

        for (int strategy = 0; strategy < STRATEGY_COUNT; strategy++) {
            percentages[strategy].push_back(
                100.0 * populationHistory[generation][strategy]
                / totalPopulation
            );
        }
    }

    cout << "Population history ready; opening Matplot++ graph.\n";

    matplot::plot(generations, percentages[0]);
    matplot::hold(matplot::on);

    for (int strategy = 1; strategy < STRATEGY_COUNT; strategy++) {
        matplot::plot(generations, percentages[strategy]);
    }

    matplot::xlabel("Generation");
    matplot::ylabel("Population (%)");
    matplot::title("Evolution of Prisoner's Dilemma Strategies");
    matplot::legend(STRATEGY_NAMES);
    matplot::grid(matplot::on);
    matplot::ylim({0, 100});

    // Clear the newline left by the final numeric input so cin.get()
    // below actually waits for the user after the graph closes.
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    matplot::show();

    cout << "Press ENTER to exit...\n";
    cin.get();
}

void printPopulationHistory(const vector<vector<int>>& populationHistory) {
    cout << "\nPOPULATION HISTORY\n";
    cout << "------------------\n";

    for (int generation = 0;
         generation < static_cast<int>(populationHistory.size());
         generation++) {
        cout << "Generation " << generation << "\n";

        for (int strategy = 0; strategy < STRATEGY_COUNT; strategy++) {
            cout << left << setw(22) << STRATEGY_NAMES[strategy]
                 << populationHistory[generation][strategy] << "\n";
        }

        cout << "-----------------------------\n";
    }
}

int readIntegerInRange(const string& prompt, int minimum, int maximum) {
    int value;

    while (true) {
        cout << prompt;

        if (cin >> value && value >= minimum && value <= maximum) {
            return value;
        }

        cout << "Invalid input. Enter an integer between "
             << minimum << " and " << maximum << ".\n";

        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    }
}

double readDoubleInRange(
    const string& prompt,
    double minimum,
    double maximum
) {
    double value;

    while (true) {
        cout << prompt;

        if (cin >> value && isfinite(value) &&
            value >= minimum && value <= maximum) {
            return value;
        }

        cout << "Invalid input. Enter a value between "
             << minimum << " and " << maximum << ".\n";

        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    }
}

int main() {
    cout << "ITERATED PRISONER'S DILEMMA: EVOLUTIONARY SIMULATION\n\n";

    cout << "Payoffs: C/C = 3 each, C/D = 0 for C and 5 for D, D/D = 0 each.\n";
    cout << "Strategies: Tit for Tat, Grim Trigger, Always Cooperate, "
            "Always Defect, Random.\n\n";

    cout << "Execution error: probability that an intended move is flipped.\n";
    cout << "Forgiveness: probability of a forgiving response by Tit for Tat, "
            "or of Grim Trigger resetting after it has been triggered.\n";
    cout << "These probabilities are independent and range from 0 to 1.\n\n";

    int seed = readIntegerInRange(
        "Random seed (1-2147483647; reuse it to reproduce a run): ",
        1, 2147483647
    );
    mt19937 rng(static_cast<unsigned int>(seed));
    cout << "Random seed: " << seed << "\n\n";

    int rounds = readIntegerInRange(
        "Rounds per game (20-50): ", 20, 50
    );

    int generations = readIntegerInRange(
        "Number of generations (1-500): ", 1, 500
    );

    vector<int> population(STRATEGY_COUNT, 0);

    while (true) {
        cout << "\nEnter the initial number of players for each strategy.\n";

        int totalPopulation = 0;

        for (int i = 0; i < STRATEGY_COUNT; i++) {
            population[i] = readIntegerInRange(
                STRATEGY_NAMES[i] + " (0-1000): ", 0, 1000
            );
            totalPopulation += population[i];
        }

        if (totalPopulation >= 500 && totalPopulation <= 1000) {
            break;
        }

        cout << "Total population must be between 500 and 1000. "
                "Please enter the composition again.\n";
    }

    double alpha = readDoubleInRange(
        "\nSelection intensity alpha (0-1; 0=no selection, 1=full selection): ",
        0.0, 1.0
    );

    double errorRate = readDoubleInRange(
        "Execution error probability (0-1; use 0 for no errors): ",
        0.0, 1.0
    );

    double forgiveness = readDoubleInRange(
        "Forgiveness probability (0-1; use 0 for no forgiveness): ",
        0.0, 1.0
    );

    cout << "\nEach strategy matchup is sampled " << MATCHUP_TRIALS
         << " times per generation to estimate its average payoff.\n";
    cout << "Running simulation...\n";

    const int initialTotalPopulation =
        accumulate(population.begin(), population.end(), 0);

    vector<vector<int>> populationHistory;
    populationHistory.push_back(population);

    for (int generation = 0; generation < generations; generation++) {
        vector<double> fitness = executeGeneration(
            population, rounds, errorRate, forgiveness, rng
        );

        population = scalePopulation(fitness, population, alpha);
        populationHistory.push_back(population);

        int checkTotal = 0;
        for (int count : population) {
            checkTotal += count;
        }

        if (checkTotal != initialTotalPopulation) {
            cerr << "ERROR: population total changed unexpectedly.\n";
            return 1;
        }
    }

    plotit(populationHistory);
    printPopulationHistory(populationHistory);

    return 0;
}
