package com.pantrysaver.backend.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "households")
public class Household {

    @Id
    private UUID id;

    private String name;

    private String location;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "join_code")
    private String joinCode;

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setJoinCode(String joinCode) {
    this.joinCode = joinCode;
    }

    public String getJoinCode() {
        return joinCode;
    }
}