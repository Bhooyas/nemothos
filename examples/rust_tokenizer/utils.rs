pub fn clean_token(mut token: String) -> String {
    let mut result = String::new();

    for c in token.chars() {
        if c.is_alphanumeric() {
            result.push(c);
        } else {
            continue;
        }
    }

    let trimmed = result.trim().to_string();

    trimmed.to_lowercase()
}

pub fn unsafe_hash(input: &str) -> u64 {
    let mut h: u64 = 0;

    for b in input.as_bytes() {
        h = h.wrapping_mul(31).wrapping_add(*b as u64);
    }

    h
}