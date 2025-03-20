import heapq
import math
import time
import sys


# Wheel-Heap Algorithm (WHA)
def load_initial_special_primes(file_path):
    """Load initial special primes from a file."""
    try:
        with open(file_path, 'r') as f:
            primes = {int(line.strip()) for line in f if line.strip()}
            return primes
    except FileNotFoundError:
        return set()


class DynamicPrimeGenerator:
    def __init__(self, max_v_squared):
        self.max_special_prime = int(math.isqrt(max_v_squared))
        self.current_number = 5
        self.extracted_primes = []
        self.semiprimes_heap = []
        self.heappush = heapq.heappush
        self.heappop = heapq.heappop
        self.allowed_residues = {1, 2, 4, 7, 8, 11, 13, 14}
        self.increments = [2, 4]
        self.inc_idx = 0

        self.special_primes = load_initial_special_primes("special_primes.txt")
        self.special_primes = {p for p in self.special_primes if p <= self.max_special_prime}

        for p in self.special_primes:
            if p >= 7:
                self._add_semiprime(p)

    def _add_semiprime(self, p):
        initial_sp = 7 * p
        self.heappush(self.semiprimes_heap, (initial_sp, p, 4 * p))

    def generate_primes(self):
        try:
            while True:
                self.current_number += self.increments[self.inc_idx]
                self.inc_idx = (self.inc_idx + 1) % 2

                if self.current_number % 15 not in self.allowed_residues:
                    continue

                skip = False
                while self.semiprimes_heap and self.semiprimes_heap[0][0] <= self.current_number:
                    sp, p, step = self.heappop(self.semiprimes_heap)
                    if sp == self.current_number:
                        skip = True
                    new_step = 2 * p if step == 4 * p else 4 * p
                    self.heappush(self.semiprimes_heap, (sp + step, p, new_step))

                if not skip:
                    self.extracted_primes.append(self.current_number)
                    if self.current_number <= self.max_special_prime and self.current_number not in self.special_primes:
                        self.special_primes.add(self.current_number)
                        if self.current_number >= 7:
                            self._add_semiprime(self.current_number)

                    if len(self.extracted_primes) % 10_000 == 0:
                        print(f"Generated {len(self.extracted_primes)} primes. Current: {self.current_number}")

        except KeyboardInterrupt:
            print("\nWHA stopped by user")
            return self.extracted_primes


# Sieve of Eratosthenes (SE)
def sieve_of_eratosthenes(n):
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            sieve[i * i: n + 1: i] = [False] * len(sieve[i * i: n + 1: i])
    return [i for i, is_prime in enumerate(sieve) if is_prime]


# Comparison & Analysis
def compare_results(wha_primes, se_primes):
    wha_set = set(wha_primes)
    se_set = set(se_primes)

    false_positives = [num for num in wha_primes if num not in se_set]
    missed_primes = [num for num in se_primes if num not in wha_set]

    return {
        "false_positives": false_positives,
        "missed_primes": missed_primes,
        "false_positive_rate": len(false_positives) / len(wha_primes) if wha_primes else 0,
        "total_primes_se": len(se_primes),
        "total_primes_wha": len(wha_primes)
    }


# ---------------------- Main Execution ----------------------
if __name__ == "__main__":
    # Get WHA parameters
    while True:
        try:
            max_v_input = input("Enter max_v_squared (e.g., 1000000000000): ").replace(' ', '')
            max_v_squared = int(eval(max_v_input.replace('^', '**')))
            if max_v_squared < 49:
                print("Value must be at least 49 (7²)")
                continue
            break
        except:
            print("Invalid input. Please enter an integer.")

    # Run WHA
    generator = DynamicPrimeGenerator(max_v_squared)
    print("\nRunning WHA. Press Ctrl+C to stop and compare with Sieve of Eratosthenes...")
    start_time = time.time()

    try:
        wha_primes = generator.generate_primes()
    finally:
        runtime = time.time() - start_time
        print(f"\nWHA Runtime: {runtime:.2f} seconds")

        if wha_primes:
            max_prime = wha_primes[-1]
            print(f"Largest WHA Prime: {max_prime}")
            print(f"Total WHA Primes: {len(wha_primes)}")

            # Run SE up to max_prime
            print("\nRunning Sieve of Eratosthenes...")
            se_start = time.time()
            se_primes = sieve_of_eratosthenes(max_prime)
            se_runtime = time.time() - se_start
            print(f"SE Runtime: {se_runtime:.2f} seconds")
            print(f"Total SE Primes: {len(se_primes)}")

            # Compare results
            results = compare_results(wha_primes, se_primes)

            print("\n--- Results ---")
            print(f"False Positives: {len(results['false_positives'])}")
            print(f"Missed Primes: {len(results['missed_primes'])}")
            print(f"False Positive Rate: {results['false_positive_rate'] * 100:.4f}%")

            # Save results
            with open("false_positives.txt", "w") as f:
                f.write("\n".join(map(str, results['false_positives'])))
            with open("missed_primes.txt", "w") as f:
                f.write("\n".join(map(str, results['missed_primes'])))
        else:
            print("No primes generated for comparison")
