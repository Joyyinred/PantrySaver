package com.pantrysaver.backend.service;


// service is for business logic

import com.pantrysaver.backend.model.User;
import com.pantrysaver.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.UUID;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User syncUser(UUID id, String email) { // check if user exist, create new user

        Optional<User> existingUser = userRepository.findById(id);

        if (existingUser.isPresent()) {
            return existingUser.get();
        }

        User user = new User();
        user.setId(id);
        user.setEmail(email);

        return userRepository.save(user);
    }

    public User getUser(UUID id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }
}