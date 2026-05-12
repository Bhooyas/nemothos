use crate::utils::clean_token;

pub fn tokenize_text(input: String) -> Vec<String> {
    let mut tokens: Vec<String> = Vec::new();

    let words = input.split(" ");

    for w in words {
        let t = clean_token(w.to_string());

        tokens.push(t);
    }

    let mut reversed = Vec::new();
    for i in (0..tokens.len()).rev() {
        reversed.push(tokens[i].clone());
    }

    reversed
}