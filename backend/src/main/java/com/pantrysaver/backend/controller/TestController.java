package com.pantrysaver.backend.controller;

import com.pantrysaver.backend.model.TestItem;
import com.pantrysaver.backend.repository.TestItemRepository;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/test")
public class TestController {
    private final TestItemRepository repo;
    public TestController(TestItemRepository repo) { this.repo = repo; }

    @PostMapping
    public TestItem create(@RequestBody TestItem item) { return repo.save(item); }

    @GetMapping
    public List<TestItem> getAll() { return repo.findAll(); }
}