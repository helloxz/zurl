<template>
    <div class="setting">
        <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
            <el-tab-pane :label="$t('site.settings')" name="wp">
                <!-- <Notice>
                    <ul>
                        <li>如果您将WP2AI和WordPress安装在同一服务器，并使用HOST网络，数据库地址一般为 <code>localhost</code> 或 <code>127.0.0.1</code> </li>
                        <li>如果WP2AI与WordPress不在同一服务器，数据库需要开启远程访问，并填写公网IP</li>
                        <li>数据库端口默认使用 <code>3306</code> 暂不支持自定义端口</li>
                        <li>如果文章扫描失败，通常是数据库信息填写不正确导致</li>
                    </ul>
                </Notice> -->
                <el-form style="margin-top:1em;" ref="siteRuleRef" :rules="rules" :model="siteForm" label-position="top">
                    <el-form-item :label="$t('title')" prop="title">
                        <el-input :placeholder="$t('setting.title.placeholder')" v-model="siteForm.title"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('keywords')" prop="keywords">
                        <el-input :placeholder="$t('setting.keywords.placeholder')" v-model="siteForm.keywords"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('description')" prop="description">
                        <el-input  type="textarea" :placeholder="$t('setting.description.placeholder')" v-model="siteForm.description"></el-input>
                    </el-form-item>
                    <el-form-item :label="$t('custom.header')" prop="header">
                        <el-input type="textarea" :placeholder="$t('setting.header.placeholder')" v-model="siteForm.header"></el-input>
                    </el-form-item>

                    <el-form-item :label="$t('custom.footer')" prop="footer">
                        <el-input type="textarea" :placeholder="$t('setting.footer.placeholder')" v-model="siteForm.footer"></el-input>
                    </el-form-item>

                    <el-form-item :label="$t('setting.allow_guest_shorten')">
                        <el-switch v-model="siteForm.allow_guest_shorten" :active-value="true" :inactive-value="false" />
                        <span class="form-hint">{{ siteForm.allow_guest_shorten ? $t('setting.allow_guest_shorten.yes') : $t('setting.allow_guest_shorten.no') }}</span>
                    </el-form-item>

                    <el-form-item>
                        <el-button @click="setSite" type="primary">{{ $t('save') }}</el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>
            
        </el-tabs>
    </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import req, { toForm } from '@/utils/req'
import { useSiteStore } from '@/stores/site'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t, locale } = useI18n()

const siteStore = useSiteStore()
const activeName = ref('wp')

// 表单属性
const siteRuleRef = ref(null);

const siteForm = ref({
    title: "",
    keywords: "",
    description: "",
    header: "",
    footer: "",
    allow_guest_shorten: true
})

// 校验规则
const rules = reactive({
    "title": [
        { required: true, message: t('setting.rules.title.required'), trigger: 'blur' },
        { min: 3, max: 32, message: t('setting.rules.length'), trigger: 'blur' },
    ]
});



// 设置站点信息
const setSite = ()=>{
    if (!siteRuleRef.value) return;
    // 验证没通过
    siteRuleRef.value.validate((valid) => {
        if (valid) {
            // 验证通过
            // 获取表单数据
            const formStr = {
                "title": siteForm.value.title,
                "keywords": siteForm.value.keywords,
                "description": siteForm.value.description,
                "header": siteForm.value.header,
                "footer": siteForm.value.footer,
                "allow_guest_shorten": siteForm.value.allow_guest_shorten !== false
            }
            const dataContent = {
                "key":"site_info",
                "value":JSON.stringify(formStr)
            }
            
            // 发送请求
            req.post("/api/option/set",toForm(dataContent))
            .then(res=>{
                if( res.data.code == 200 ) {
                    // siteStore.wp_domain = formData.value['wordpress.domain']
                    // 提示成功
                    ElMessage.success(t('setting.update.success'))
                    // 清空缓存
                    // siteStore.app_info = {}
                    // sessionStorage.removeItem("app_info")
                }
                else{
                    // 提示错误
                    ElMessage.error(res.data.msg)
                }
            })
            .catch(err=>{
                // 提示错误
                ElMessage.error(t('setting.fail'))
            })
        } else {
            return false;
        }
    });
}

// 获取配置信息（合并默认值，保证 allow_guest_shorten 等新字段有默认值）
const getSetting = () => {
    siteStore.getSiteInfo().then(() => {
        siteForm.value = {
            title: "",
            keywords: "",
            description: "",
            header: "",
            footer: "",
            allow_guest_shorten: true,
            ...siteStore.site_info,
        }
    })
}

onMounted (()=>{
    getSetting()
})
</script>

<style scoped>
.setting {
    width: 600px;
}
.form-hint {
    margin-left: 8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
}
</style>