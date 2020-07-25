# txrestserver

A twisted-python REST server that supports authentication.

## Release History

| Version | Notes       |
| :-----: | :---------- |
|   0.0.1 | Initial pre-release (Alpha) with basic access authentication Support

## Authentication Support
Currently only Basic authentication is supported but digest and certificate support is planned.

**Note**: Authentication descriptions below are from Wikipedia.

### Basic Authentication
In the context of an HTTP transaction, 
[basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication)
is a method for an HTTP user agent (e.g. a web browser) to provide a user name and password
when making a request. In basic HTTP authentication, a request contains a header field in the
form of Authorization: Basic <credentials>, where credentials is the Base64 encoding of ID
and password joined by a single colon :.

### Digest Authentication
[Digest access authentication](https://en.wikipedia.org/wiki/Digest_access_authentication)
is one of the agreed-upon methods a web server can use to
negotiate credentials, such as username or password, with a user's web browser. This
can be used to confirm the identity of a user before sending sensitive information,
such as online banking transaction history. It applies a hash function to the username
and password before sending them over the network. In contrast, basic access
authentication uses the easily reversible Base64 encoding instead of hashing, making
it non-secure unless used in conjunction with TLS.

Technically, digest authentication is an application of MD5 cryptographic hashing with
usage of nonce values to prevent replay attacks. It uses the HTTP protocol.

### JSON Web Token
[JSON Web Token](https://en.wikipedia.org/wiki/JSON_Web_Token) is an Internet standard
for creating data with optional signature and/or optional encryption whose payload holds
JSON that asserts some number of claims. The tokens are signed either using a private
secret or a public/private key. For example, a server could generate a token that has
the claim "logged in as admin" and provide that to a client. The client could then use
that token to prove that it is logged in as admin. The tokens can be signed by one
party's private key (usually the server's) so that party can subsequently verify the
token is legitimate. If the other party, by some suitable and trustworthy means, is in
possession of the corresponding public key, they too are able to verify the token's
legitimacy. The tokens are designed to be compact, URL-safe, and usable especially
in a web-browser single-sign-on (SSO) context. JWT claims can typically be used to pass
identity of authenticated users between an identity provider and a service provider,
or any other type of claims as required by business processes.

JWT relies on other JSON-based standards: JSON Web Signature and JSON Web Encryption.

### TLS-SRP
[Transport Layer Security Secure Remote Password (TLS-SRP)](https://en.wikipedia.org/wiki/TLS-SRP)
ciphersuites are a set of cryptographic protocols that provide secure communication based
on passwords, using an SRP password-authenticated key exchange.

There are two classes of TLS-SRP ciphersuites: The first class of cipher suites uses only
SRP authentication. The second class uses SRP authentication and public key certificates
together for added security.

Usually, TLS uses only public key certificates for authentication. TLS-SRP uses a value
derived from a password (the SRP verifier) and a salt, shared in advance among the
communicating parties, to establish a TLS connection. There are several possible reasons
one may choose to use TLS-SRP:

Using password-based authentication does not require reliance on certificate authorities.

 - The end user does not need to check the URL being certified. If the server does not
   know data derived from the password then the connection simply cannot be made. This
   prevents Phishing.
   
 - Password authentication is less prone than certificate authentication to certain types
   of configuration mistakes, such as expired certificates or mismatched common name fields.
   
 - TLS-SRP provides mutual authentication (the client and server both authenticate each
   other), while TLS with server certificates only authenticates the server to the client.
   Client certificates can authenticate the client to the server, but it may be easier for
   a user to remember a password than to install a certificate.

## Examples

[Examples](https://github.com/cboling/txrestserver/examples) are available on Github
