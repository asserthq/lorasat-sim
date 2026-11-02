#[path = "../../output/gen/db.rs"]
mod db;

use std::net::UdpSocket;

fn main() {
    let socket = UdpSocket::bind((db::COM_ADDRESS, db::COM_PORT)).unwrap();
    println!("[+] Слушаю {}:{}", db::COM_ADDRESS, db::COM_PORT);

    let mut buf = [0u8; db::DB_SIZE];

    loop {
        let (n, addr) = match socket.recv_from(&mut buf) {
            Ok(r) => r,
            Err(e) => {
                println!("[!] ошибка приёма: {}", e);
                continue;
            }
        };
        if n != db::DB_SIZE {
            println!("[!] пришло {} байт, ждали {}", n, db::DB_SIZE);
            continue;
        }

        let mut d: db::Db = unsafe { std::ptr::read_unaligned(buf.as_ptr() as *const db::Db) };

        match d.cmd {
            0 => println!("[Rust Init]"),
            1 => {
                println!("[Rust Run] получила: t = {}, x = {}", d.t, d.x);
                d.x += 1;
            }
            2 => println!("[Rust Fin]"),
            _ => {}
        }

        unsafe { std::ptr::write_unaligned(buf.as_mut_ptr() as *mut db::Db, d) };
        socket.send_to(&buf, addr).unwrap();
    }
}