from django.db import models


class Task(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    profiletool = models.ForeignKey('ProfileTool', on_delete=models.CASCADE, null=True, blank=True)
    status = models.ForeignKey('DirTaskStatus', on_delete=models.CASCADE, db_column='status_id')
    type = models.ForeignKey('DirTaskType', on_delete=models.CASCADE, db_column='type_id')
    description = models.TextField(blank=True, null=True)

    position = models.IntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    created = models.DateField()
    
    class Meta:
        db_table = 'task'
        managed = False
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['position', '-created']
    
    def __str__(self):
        if self.product:
            return f"Задача: {self.product.name}"
        elif self.profiletool:
            return f"Задача: {self.profiletool.profile.article}"
        return f"Задача #{self.id}"
    
    def get_display_name(self):
        """Возвращает название задачи для отображения"""
        if self.profiletool:
            return self.profiletool.profile.article
        elif self.product:
            return self.product.name
        return f"Задача #{self.id}"

class TaskComponent(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='component_list')
    profiletool_component_id = models.IntegerField(null=True, blank=True)
    product_component_id = models.IntegerField(null=True, blank=True)

    # Добавляем связи для получения имени
    @property
    def component_name(self):
        if self.profiletool_component_id:
            try:
                comp = ProfileToolComponent.objects.get(id=self.profiletool_component_id)
                return comp.type.name
            except ProfileToolComponent.DoesNotExist:
                return "—"
        elif self.product_component_id:
            try:
                comp = ProductComponent.objects.get(id=self.product_component_id)
                return comp.name
            except ProductComponent.DoesNotExist:
                return "—"
        return "—"

    class Meta:
        db_table = 'task_component'
        managed = False
        verbose_name = 'Компонент задачи'
        verbose_name_plural = 'Компоненты задач'

    def __str__(self):
        return self.component_name

class TaskComponentStage(models.Model):
    task_component = models.ForeignKey(TaskComponent, on_delete=models.CASCADE, related_name='stage_list')
    stage_name_id = models.IntegerField(null=True, blank=True)
    machine_id = models.IntegerField(null=True, blank=True)
    stage_num = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'task_component_stage'
        managed = False
        verbose_name = 'Этап работы компонента задачи'
        verbose_name_plural = 'Этапы работы компонентов задач'

class ProfileTool(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    dimension_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'profiletool'
        managed = False
        verbose_name = 'Инструмент профиля'
        verbose_name_plural = 'Инструменты профилей'
    
    def __str__(self):
        return f"Инструмент {self.id} - {self.profile.article}"

class ProfileToolComponent(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.ForeignKey('DirProfileToolComponentType', on_delete=models.DO_NOTHING, db_column='type_id')

    class Meta:
        db_table = 'profiletool_component'
        managed = False

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey('DirDepartment', on_delete=models.CASCADE)

    class Meta:
        db_table = 'product'
        managed = False
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'
    
    def __str__(self):
        return self.name

class ProductComponent(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'product_component'
        managed = False

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
    
    @property
    def css_class(self):
        """Возвращает CSS-класс в зависимости от имени статуса"""
        mapping = {
            'В работе': 'bg-primary',
            'Выполнено': 'bg-success',
            'Новая': 'bg-info'
        }
        return mapping.get(self.name, 'bg-secondary')

class DirTaskType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'dir_task_type'
        managed = False
        verbose_name = 'Тип задачи'
        verbose_name_plural = 'Типы задач'

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

class DirProfileToolComponentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'dir_profiletool_component_type'
        managed = False
