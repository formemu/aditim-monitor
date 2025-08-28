from django.db import models

class DirTaskStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'dir_task_status'
        managed = False
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
    
    def __str__(self):
        return self.name

class DirDepartment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'dir_department'
        managed = False
        verbose_name = 'Департамент'
        verbose_name_plural = 'Департаменты'
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    article = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    sketch = models.BinaryField(null=True, blank=True)
    
    class Meta:
        db_table = 'profile'
        managed = False
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return self.article

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey(DirDepartment, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'product'
        managed = False
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'
    
    def __str__(self):
        return self.name

class ProfileTool(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    dimension_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'profile_tool'
        managed = False
        verbose_name = 'Инструмент профиля'
        verbose_name_plural = 'Инструменты профилей'
    
    def __str__(self):
        return f"Инструмент {self.id} - {self.profile.article}"

class Task(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    profile_tool = models.ForeignKey(ProfileTool, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(DirDepartment, on_delete=models.CASCADE)
    status = models.ForeignKey(DirTaskStatus, on_delete=models.CASCADE, db_column='status_id')
    position = models.IntegerField(default=0)
    deadline_on = models.DateField(null=True, blank=True)
    stage = models.TextField(blank=True)
    created_at = models.DateTimeField()
    
    class Meta:
        db_table = 'task'
        managed = False
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['position', '-created_at']
    
    def __str__(self):
        if self.product:
            return f"Задача: {self.product.name}"
        elif self.profile_tool:
            return f"Задача: {self.profile_tool.profile.article}"
        return f"Задача #{self.id}"
    
    def get_display_name(self):
        """Возвращает название задачи для отображения"""
        if self.profile_tool:
            return self.profile_tool.profile.article
        elif self.product:
            return self.product.name
        return f"Задача #{self.id}"

class TaskComponent(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='component_list')
    profile_tool_component_id = models.IntegerField(null=True, blank=True)
    product_component_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'task_component'
        managed = False
        verbose_name = 'Компонент задачи'
        verbose_name_plural = 'Компоненты задач'
