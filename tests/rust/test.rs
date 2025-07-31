let foo = 12;
let bar = 13;
if foo == bar {
  println!("foo = bar");
} else if foo < bar {
  println!("foo < bar");
} else if foo != bar {
  println!("foo != bar");
} else {
  println!("Nothing");
}

enum IpAddrKind {
  V4,
  V6,
}
struct IpAddr {
  kind: IpAddrKind,
  address: String,
}

fn main(){
    let ip = IpAddr{
        kind: IpAddrKind::V4,
        address: String::from("127.0.0.1")
    };
}