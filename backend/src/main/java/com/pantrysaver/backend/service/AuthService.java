package com.pantrysaver.backend.service;

// supabase use JWT for authentication
// supabase create jwt and return it to flet, flet stores it and send to backend to verify it 

import com.auth0.jwt.JWT; 
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class AuthService {

    @Value("${supabase.jwt.secret}")
    private String jwtSecret;

    public DecodedJWT validateToken(String token) {  // check if this JWT is real and valid

        Algorithm algorithm = Algorithm.HMAC256(jwtSecret);

        return JWT.require(algorithm)
                .build()
                .verify(token);
    }

    public UUID extractUserId(DecodedJWT jwt) {
        return UUID.fromString(jwt.getSubject());
    }

    public String extractEmail(DecodedJWT jwt) {
        return jwt.getClaim("email").asString();
    }
}
