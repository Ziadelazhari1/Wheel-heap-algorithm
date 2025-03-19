import heapq
import math
import time


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

        # Initialize special primes
        self.special_primes = load_initial_special_primes("special_primes.txt")
        self.special_primes = {p for p in self.special_primes if p <= self.max_special_prime}

        # Initialize semiprimes for valid special primes (>=7)
        for p in self.special_primes:
            if p >= 7:
                self._add_semiprime(p)

    def _add_semiprime(self, p):
        """Add semiprimes for a new special prime"""
        initial_sp = 7 * p
        self.heappush(self.semiprimes_heap, (initial_sp, p, 4 * p))

    def generate_primes(self):
        try:
            while True:
                # Generate next candidate
                self.current_number += self.increments[self.inc_idx]
                self.inc_idx = (self.inc_idx + 1) % 2

                # Skip multiples of 3/5
                if self.current_number % 15 not in self.allowed_residues:
                    continue

                # Check semiprimes heap
                skip = False
                while self.semiprimes_heap and self.semiprimes_heap[0][0] <= self.current_number:
                    sp, p, step = self.heappop(self.semiprimes_heap)
                    if sp == self.current_number:
                        skip = True
                    new_step = 2 * p if step == 4 * p else 4 * p
                    self.heappush(self.semiprimes_heap, (sp + step, p, new_step))

                if not skip:
                    self.extracted_primes.append(self.current_number)

                    # Add to special primes if within limit
                    if self.current_number <= self.max_special_prime:
                        if self.current_number not in self.special_primes:
                            self.special_primes.add(self.current_number)
                            if self.current_number >= 7:
                                self._add_semiprime(self.current_number)

                    # Progress reporting
                    if len(self.extracted_primes) % 10_000 == 0:
                        print(f"Generated {len(self.extracted_primes)} primes. Current: {self.current_number}")

        except KeyboardInterrupt:
            print("\nStopped by user")
            return self.extracted_primes


if __name__ == "__main__":
    # Get user input with safety checks
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

    generator = DynamicPrimeGenerator(max_v_squared)
    start_time = time.time()

    try:
        primes = generator.generate_primes()
    finally:
        runtime = time.time() - start_time
        print(f"\nTotal runtime: {runtime:.2f} seconds")
        print(f"Generated {len(primes)} primes")
        print(f"Largest prime: {primes[-1] if primes else None}")

        # Save all generated primes
        with open("full_output4.txt", "w") as f:
            for num in primes:
                f.write(f"{num}\n")

        # Save special primes up to max_special_prime
        with open("special_primes.txt", "w") as f:
            for p in sorted(generator.special_primes):
                f.write(f"{p}\n")
