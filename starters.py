import random
import math
import collections
from concurrent.futures import ProcessPoolExecutor

# Cache for entropy calculations to avoid redundant work
ENTROPY_CACHE = {}

def get_starter():
    """Return an optimal starter word based on entropy calculation"""
    # Default starters in case calculation fails or is disabled
    default_starters = ["slate", "crane", "trace", "slant", "crate"]
    
    try:
        # Load the cached best starters if available
        return get_cached_best_starter() or random.choice(default_starters)
    except:
        return random.choice(default_starters)

def get_cached_best_starter():
    """Get the cached best starter word, if available"""
    try:
        with open("words/best_starters.txt", "r") as f:
            starters = f.read().strip().split("\n")
            if starters:
                return starters[0]  # Return the top starter
    except FileNotFoundError:
        return None

def calculate_pattern(guess, answer):
    """Calculate the Wordle pattern (G/Y/.) for a guess against a potential answer"""
    pattern = []
    for i, letter in enumerate(guess):
        if letter == answer[i]:
            pattern.append('G')  # Green
        elif letter in answer:
            pattern.append('Y')  # Yellow
        else:
            pattern.append('.')  # Gray
    return ''.join(pattern)

def calculate_word_entropy(word, word_list):
    """Calculate entropy (information gain) for a word against potential solutions"""
    if word in ENTROPY_CACHE:
        return ENTROPY_CACHE[word]
        
    patterns = {}
    for potential_answer in word_list:
        pattern = calculate_pattern(word, potential_answer)
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    total = len(word_list)
    entropy = 0
    for count in patterns.values():
        probability = count / total
        entropy -= probability * (math.log2(probability))
    
    # Cache the result
    ENTROPY_CACHE[word] = entropy
    return entropy

def analyze_letter_frequency(word_list):
    """Analyze letter frequency in the word list to prioritize common letters"""
    # Overall letter frequency
    all_letters = ''.join(word_list)
    letter_freq = collections.Counter(all_letters)
    
    # Positional letter frequency
    pos_freq = [collections.Counter() for _ in range(5)]
    for word in word_list:
        for i, letter in enumerate(word):
            pos_freq[i][letter] += 1
    
    return letter_freq, pos_freq

def calculate_starter_score(word, letter_freq, pos_freq, word_list):
    """Calculate a combined score for a word based on entropy and letter frequency"""
    # Weight factors (can be adjusted)
    ENTROPY_WEIGHT = 0.7
    FREQ_WEIGHT = 0.3
    
    # Calculate entropy score
    entropy = calculate_word_entropy(word, word_list)
    max_entropy = 6.0  # Approximate maximum possible entropy
    entropy_score = entropy / max_entropy
    
    # Calculate frequency score
    unique_letters = set(word)
    freq_score = sum(letter_freq[letter] for letter in unique_letters) / (5 * len(word_list))
    
    # Calculate positional score
    pos_score = sum(pos_freq[i][letter] for i, letter in enumerate(word)) / (5 * len(word_list))
    
    # Penalize for duplicate letters
    unique_penalty = 1.0 if len(unique_letters) == 5 else (0.8 + 0.04 * len(unique_letters))
    
    # Combine scores
    combined_score = (ENTROPY_WEIGHT * entropy_score + 
                      FREQ_WEIGHT * (0.6 * freq_score + 0.4 * pos_score)) * unique_penalty
    
    return combined_score, entropy

def find_best_starters(top_n=10):
    """Find the best starter words based on entropy and letter frequency"""
    try:
        # Load the main word list
        with open("words/wordle_words.txt", "r") as f:
            word_list = f.read().strip().split()
        
        # Also check the already used list to influence our decision
        try:
            with open("words/already_used.txt", "r") as f:
                used_words = set(f.read().strip().split())
                # Consider already used words less likely to be answers
                # but don't completely exclude them
        except FileNotFoundError:
            used_words = set()
        
        print("Analyzing letter frequency...")
        letter_freq, pos_freq = analyze_letter_frequency(word_list)
        
        # Parallel processing for faster calculation
        print(f"Calculating scores for {len(word_list)} words...")
        word_scores = {}
        
        # Process in batches to avoid excessive parallelism
        batch_size = 500
        for i in range(0, len(word_list), batch_size):
            batch = word_list[i:i+batch_size]
            for word in batch:
                # Reduce score slightly if the word has been used before
                penalty = 0.9 if word.upper() in used_words else 1.0
                score, entropy = calculate_starter_score(word, letter_freq, pos_freq, word_list)
                word_scores[word] = (score * penalty, entropy)
        
        # Sort by score in descending order
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1][0], reverse=True)
        
        # Save the top N starters
        best_starters = [word for word, _ in sorted_words[:top_n]]
        with open("words/best_starters.txt", "w") as f:
            f.write('\n'.join(best_starters))
        
        print(f"Top {top_n} starter words:")
        for i, (word, (score, entropy)) in enumerate(sorted_words[:top_n], 1):
            print(f"{i}. {word} (Score: {score:.4f}, Entropy: {entropy:.4f})")
        
        return best_starters[0]  # Return the top starter
    
    except Exception as e:
        print(f"Error finding best starters: {e}")
        return "slate"  # Default fallback

if __name__ == "__main__":
    # When run directly, calculate and save the best starters
    find_best_starters()
