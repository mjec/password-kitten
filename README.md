# password-kitten

A password manager for kitty (https://sw.kovidgoyal.net/kitty/)

## Why are all the dependencies here?

This is super gross, but it contains all the files required to
run a quick-and-dirty password manager in kitty. Because kitty
uses its own built-in python interpreter, we don't have access
to anything on the normal PTYHONPATH. Instead of solving this,
I have opted to just include all the requirements here. This
is kind of okay, I guess?

Specifically, we include:

 * prompt_toolkit-2.0.7
 * six 1.12.0 (dependency of prompt_toolkit)
 * wcwidth-0.1.7 (dependency of prompt_toolkit)
 * keyring-17.1.1 (with dependency on entrypoints removed)
 * appdirs-1.4.3

The patch to keyring is included as the file `keyring.patch`.

Why remove the entrypoints dependency? Because these packages
aren't really installed, we don't have the metadata entrypoints
relies on, so it doesn't work. It therefore becomes vestigial,
and so I removed it.

This also means you can't add a new keyring backend just by
installing the package; you have to edit `keyring/backend.py`
to import it directly.

## Licensing

Each of these modules is subject to its own copyright, despite
the source being included in this repository.

This project is licensed under the GNU GPL 3.0 (as descirbed
in the LICENSE file), but that **only** applies to the
following files:

 * keyring.patch
 * password.py

## Usage

Install by copying all the files from the repository into your
kitty config directory. (I know.)

Add shortcut keys to print out passwords, create new ones
and delete existing ones.

For print and delete, you can autocomplete password names
using tab.

What I have for this in my kitty.conf:

```
map ctrl+p kitten password.py print
map ctrl+shift+p kitten password.py create
map ctrl+shift+super+p kitten password.py delete
```

## Security

Using keychain, we use your built-in operating system's
secure credential storage. This means you should be relatively
protected against other apps accessing this storage.

However, we use OS pipes and kittens are an inherently
insecure medium, because they are designed for interprocess
communication. As such, this is only as secure as the least
secure of the following:

 * all of the included modules;
 * the python interpreter in kitty;
 * kitty itself;
 * pipes/proc/IPC generally;
 * your operating system's storage;
 * the ability for any application to run kitty.

This doesn't have any protection against kitty being run in
kitten mode directly, and just piping out all the passwords.

The list of passwords is stored in your user data dir with
permissions 600 (read/write by user only) but we don't check
that it hasn't been modified/maliciously created in advance.

So this is _slightly_ more secure than a text document, but
not that much more secure.

## Development

Pull requests are very welcome.

Tested on macOS 10.14.2 (Mojave) only.
