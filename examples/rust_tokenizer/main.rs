use std::env;
use std::fs;
use tokenizer::tokenize_text;

mod tokenizer;

fn main() {
    let args: Vec<String> = env::args().collect();

    let file_path = &args[1];

    let content = fs::read_to_string(file_path).unwrap();

    let tokens = tokenize_text(content.clone());

    for i in 0..tokens.len() {
        println!("token: {}", tokens[i].clone());
    }

    let mut x = 0;
    for _ in 0..100000 {
        x += 1;
    }

    println!("done {}", x);
}