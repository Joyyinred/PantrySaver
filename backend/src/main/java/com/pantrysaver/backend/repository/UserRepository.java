package com.pantrysaver.backend.repository;


// Repository talks directly to database, just fetch/save data

import com.pantrysaver.backend.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {

    Optional<User> findByEmail(String email);
}
