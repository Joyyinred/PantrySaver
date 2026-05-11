package com.pantrysaver.backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.pantrysaver.backend.model.TestItem;

public interface TestItemRepository extends JpaRepository<TestItem, Long> {}
